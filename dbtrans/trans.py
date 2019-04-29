import urllib

# from django.contrib.gis.gdal import field
from django.contrib.sites import requests
from django.utils.translation import get_language
from .functions import get_avaiable_languages, avaiable_languages_without_default
from .models import TranslatedField
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models.signals import post_save, pre_save, post_delete


DEFAULT_LANGUAGE = settings.LANGUAGE_CODE.lower()


def default_action(fake_fields, field):
    """
    DEFINE WHAT ACTION TO DO WHEN THERE IS NO TRANSLATION
    Default action is returning the same value
    """

    return getattr(fake_fields[field.attname], DEFAULT_LANGUAGE)


class Trans(object):
    def __init__(self, klass, fields):
        self.klass = klass
        self.default_language = get_language()
        self.fields = fields



        self.klass.translated_fields = []
        self.set_methods()

    def init_method(self):
        def __init__(self, *args, **kwargs):
            from .fakeField import FakeField
            fake = {}
            for f in self.translated_fields:
                fake[f.attname] = FakeField(get_avaiable_languages())
            super(self._meta.model, self).__setattr__(
                'fake_fields', {f.attname: FakeField(get_avaiable_languages()) for f in self.translated_fields}
            )
            super(self._meta.model, self).__init__(*args, **kwargs)
            f = [f.attname for f in self.translated_fields]
            ct = ContentType.objects.get_for_model(model=self)
            x = TranslatedField.objects.filter(ct=ct.id).exclude(field__in=f)
            if len(x) > 0:
                TranslatedField.objects.filter(ct=ct.id, field=x.first().field).delete()

        return __init__

    def getter_method(self, field):
        def getter(self):
            lang = get_language().lower()
            if self.id:
                if self.fake_fields[field.attname].loaded:
                    ret = getattr(self.fake_fields[field.attname], lang)
                else:
                    t = TranslatedField.objects.get(
                        ct=ContentType.objects.get_for_model(self._meta.model),
                        obj_id=self.id,
                        field=field.attname,
                    )
                    setattr(self.fake_fields[field.attname], lang, t.translation())
                    ret = getattr(self.fake_fields[field.attname], lang)
            else:
                if self.fake_fields[field.attname].loaded:
                    ret = getattr(self.fake_fields[field.attname], lang)
                else:
                    # I think is never reachable
                    ret = self.__dict__[field.attname]
            if ret == "" and lang != DEFAULT_LANGUAGE:
                return default_action(self.fake_fields, field)
            return ret
        return getter

    def setter_method(self):
        def setter(self, key, value):
            if key in [f.attname for f in self.translated_fields]:
                lang = get_language().lower()
                if not self.fake_fields[key].loaded:
                    setattr(self.fake_fields[key], DEFAULT_LANGUAGE, value)
                    self.__dict__[key] = value
                if self.id and not self.fake_fields[key].loaded:
                    ct = ContentType.objects.get_for_model(self._meta.model)
                    if not TranslatedField.check_if_field_is_translated(ct, self.id, key):
                        TranslatedField.register_new_field(ct, self.id, key)
                    t = TranslatedField.objects.get(
                        ct=ContentType.objects.get_for_model(self._meta.model),
                        obj_id=self.id,
                        field=key
                    )
                    for l in avaiable_languages_without_default():
                        try:
                            setattr(self.fake_fields[key], l[0], t.translation_set.get(lang_code=l[0]).translation)
                        except Exception as e:
                            print('ERROR: on trans.py line 122', e)
                            setattr(self.fake_fields[key], l[0], 'NA')

                else:
                    setattr(self.fake_fields[key], lang, value)
                self.fake_fields[key].loaded = True
                if lang == DEFAULT_LANGUAGE:
                    self.__dict__[key] = value
            else:
                super(self._meta.model, self).__setattr__(key, value)
        return setter

    @classmethod
    def before_save(cls, sender, **kwargs):
        obj = kwargs.get('instance')
        if obj.pk:
            lang = get_language().lower()
            if lang != DEFAULT_LANGUAGE:
                for f in obj.translated_fields:
                    tf = TranslatedField.objects.get(
                        ct=ContentType.objects.get_for_model(obj._meta.model),
                        obj_id=obj.id,
                        field=f.attname
                    )
                    trans = tf.translation_set.get(lang_code=lang)
                    trans.translation = getattr(obj, f.attname)
                    trans.updated = True
                    trans.save()

                model = type(obj)
                old = model.objects.get(id=obj.id)
                for f in obj.translated_fields:
                    setattr(obj, f.attname, getattr(old.fake_fields[f.attname], DEFAULT_LANGUAGE))
            else:
                for f in obj.translated_fields:
                    old = type(obj).objects.get(pk=obj.pk)
                    if old.name != obj.name:
                        tf = TranslatedField.objects.get(
                            ct=ContentType.objects.get_for_model(obj._meta.model),
                            obj_id=obj.id,
                            field=f.attname
                        )
                        [f.change() for f in tf.translation_set.all()]

    @classmethod
    def add_new_translations(cls, sender, **kwargs):
        obj = kwargs.get('instance')
        new = kwargs.get('created')
        if new:
            for f in obj.translated_fields:
                field = obj._meta.get_field(f.attname)
                tf = TranslatedField.objects.create(
                    ct=ContentType.objects.get_for_model(obj._meta.model),
                    obj_id=obj.id,
                    field=field.attname,
                )
                tf.add_new_translation(getattr(obj, "%s" % field.attname))

    @classmethod
    def after_delete(cls, sender, **kwargs):
        instance = kwargs.get('instance')
        TranslatedField.remove_translations(
            ContentType.objects.get_for_model(instance._meta.model),
            instance.id
        )

    def set_signals(self):
        pre_save.connect(self.before_save, sender=self.klass, dispatch_uid="%s_pre_save" % self.klass)
        post_save.connect(self.add_new_translations, sender=self.klass, dispatch_uid="%s_post_save" % self.klass)
        post_delete.connect(self.after_delete, sender=self.klass)

    def set_methods(self):
        self.klass.__init__ = self.init_method()
        self.klass.__setattr__ = self.setter_method()
        for field in self.fields:
            self.klass.translated_fields.append(field)
            setattr(self.klass, field.attname, property(self.getter_method(field)))
        self.set_signals()

    def model_class_with_trans(self):
        return self.klass


