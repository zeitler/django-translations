from .functions import *
from django.db import models
from .models import TranslatedField
from django.contrib.contenttypes.models import ContentType


LANG = 'l'
LOADED = 'd'


class Translate(object):
    def __init__(self, *fields):
        self.fields = fields
        self.default_language = default_language()

    def avaiable_types(self):
        #ONLY FOR CHARFIELD AND TEXTFIELD
        return [models.CharField, models.TextField, ]

    def check_if_translated_fields_are_valid(self, klass):
        avaiable_fields = []
        for field in klass._meta.fields:
            avaiable_fields.append(field.name)

        for field in self.fields:
            if field not in avaiable_fields and type(klass._meta.get_field(field)) in self.avaiable_types():
                raise SyntaxError(
                    u"%s %s %s %s" % (
                        u'The field marked for translation',
                        field,
                        u'dont exist',
                        "or isn't CharField or TextField",
                    )
                )

        if sorted(self.fields) != sorted(set(self.fields)):
            raise OverflowError(
                "You can only translate a field once"
            )

        return [klass._meta.get_field(f) for f in self.fields]

    def __call__(self, klass):
        from .trans import Trans
        fields = self.check_if_translated_fields_are_valid(klass)
        return Trans(klass, fields).model_class_with_trans()
