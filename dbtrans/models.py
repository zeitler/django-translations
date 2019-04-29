from django.db import models, IntegrityError
from django.utils.translation import ugettext as _
from .functions import default_language, get_verbose_language, avaiable_languages_without_default
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils.translation import get_language, activate
DEFAULT_LANGUAGE = settings.LANGUAGE_CODE.lower()


class TranslatedField(models.Model):
    ct = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=_(u'Modelo'))
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey("ct", "obj_id")
    field = models.CharField(max_length=50, verbose_name=_(u'Campo'))
    changed = models.BooleanField(default=True, )

    def __str__(self):
        return self.original() or 'empty value'

    def original(self):
        try:
            old = get_language()
            activate(DEFAULT_LANGUAGE)
            obj = self.ct.get_object_for_this_type(pk=self.obj_id)
            original = getattr(obj, "%s" % self.field)
            activate(old)
            return original
        except:
            return None

    @staticmethod
    def set_original_has_changed(ct, obj_id, field):
        o = TranslatedField.objects.get(ct=ct, obj_id=obj_id, field=field)
        [ts.change() for ts in o.translation_set.all()]

    @staticmethod
    def change(ct, obj_id, field, value):
        lang = get_language().lower()
        try:
            o = TranslatedField.objects.get(ct=ct, obj_id=obj_id, field=field)
            x = o.translation_set.get(lang_code=lang)
            x.translation = value
            x.updated = True
            x.save()
        except TranslatedField.DoesNotExist:
            tf = TranslatedField.objects.create(
                ct=ct,
                obj_id=obj_id,
                field=field.attname,
            )
            tf.add_new_translation()

    def add_new_translation(self, value=None):
        languages = avaiable_languages_without_default()
        success = True
        for lang, verbose in languages:
            try:
                self.translation_set.get(field=self, lang_code=lang)
            except Translation.DoesNotExist:
                self.translation_set.create(
                    field=self,
                    lang_code=lang,
                    translation=value,
                    updated=value is not None
                )
            except Exception as e:
                print(e)
                success = False
        return success

    @staticmethod
    def remove_translations(ct, obj_id):
        o = TranslatedField.objects.filter(ct=ct, obj_id=obj_id)
        for field in o:
            [d.delete() for d in field.translation_set.all()]
            field.delete()

    def translation(self):
        active_lang = get_language()
        if active_lang == default_language():
            raise("Default language is active!")
        try:
            trans = self.translation_set.get(lang_code=active_lang).translation
        except Translation.DoesNotExist:
            # print('Does not exist')
            raise("Translation don't exist")

        return trans

    @staticmethod
    def check_if_field_is_translated(ct, obj_id, field):
        return len(TranslatedField.objects.filter(ct=ct.id, obj_id=obj_id, field=field)) > 0

    @staticmethod
    def register_new_field(ct, obj_id, field):
        obj = TranslatedField.objects.create(ct=ct, obj_id=obj_id, field=field)
        obj.add_new_translation()

def get_translation_permissions():
        from .functions import avaiable_languages_without_default
        langs = avaiable_languages_without_default()
        perms = []
        for l in langs:
            perms.append(
                (('can_translate_to_%s' % l[0]),
                ((_('User can translato to %s language' % l[1])))),

            )
        return tuple(perms)


class Translation(models.Model):
    field = models.ForeignKey(TranslatedField, on_delete=models.CASCADE, verbose_name=_(u'Field'))
    lang_code = models.CharField(max_length=10, verbose_name=_('Language Code'))
    translation = models.TextField(default='', blank=True, null=True)
    updated = models.BooleanField(default=False, verbose_name=_('Fuzzy')) # when the original is changed, it turns True

    class Meta:
        unique_together = ('field', 'lang_code')
        permissions = get_translation_permissions()

    def __str__(self):
        return "Translation to %s" % get_verbose_language(self.lang_code)

    def original(self):
        return self.field

    @staticmethod
    def make_permissions():
        from django.contrib.auth.models import Permission
        ct = ContentType.objects.get_for_model(Translation)
        for p in get_translation_permissions():
            try:
                Permission.objects.create(
                    name=p[0],
                    content_type=ct,
                    codename=p[1]
                )
            except:
                pass

    def change(self):
        self.updated = False
        super().save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        super().save(force_insert, force_update, using, update_fields)

    def exist(self):
        try:
            return self.ct.objects.get(id=self.obj_id)
        except self.ct.DoesNotExist:
            return False
