from django.conf import settings
from django.utils.translation import activate
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


def avaiable_languages_without_default():
    # print(get_avaiable_languages())
    # print([get_verbose_language(l) for l in get_avaiable_languages()])
    return [(l.lower(), get_verbose_language(l)) for l in get_avaiable_languages() if l != default_language()]


def get_avaiable_languages():
    return [l[0].lower() for l in settings.LANGUAGES]


def get_verbose_language(lang):
    try:
        return dict([[l[0].lower(), l[1]] for l in settings.LANGUAGES])[lang]
    except:
        pass

def default_language():
    return settings.LANGUAGE_CODE.lower()


def confirm_languages():
    from .models import TranslatedField
    for tf in TranslatedField.objects.all():
        for lang in get_avaiable_languages():
            try:
                tf.translation_set.get(lang_code=lang)
            except:
                tf.translation_set.create(lang_code=lang)


def check_if_translations_were_created():
    """
    for cases where are data introduced before dbtrans is installed, or added through
    mysql
    It goes through all models registered and check if objects have translated fields.
    If not, it creates it
    :return:
    """
    from .models import TranslatedField
    activate(settings.LANGUAGE_CODE)
    new = 0
    # for model in [m for m in apps.get_models() if getattr(m, 'translated_fields', None) != None]:
    for model in [m for m in apps.get_models() if getattr(m, 'translated_fields', None)]:
        for field in model.translated_fields:
            try:
                ct = ContentType.objects.get_for_model(model._meta.model)
                for o in model.objects.all():
                    tf, created = TranslatedField.objects.get_or_create(
                        ct=ct.id,
                        obj_id=o.id,
                        field=field.attname
                    )
                    tf.add_new_translation()
                    if created:
                        new += 1
            except Exception as e:
                print(e)
    print('Criadas %s traduções' % new)
