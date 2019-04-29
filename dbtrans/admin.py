from django.contrib import admin
from .models import *
from .Admin.avaiableLanguagesFilter import *
from django.utils.translation import ugettext as _
from .Admin.genRelRelatedOnly import GenericRelationsRelatedOnly, GenericRelationsRelatedOnlyInSelf
from .functions import get_verbose_language
from .Admin.filters import *
from .Admin.forms import *


class TranslationInline(admin.TabularInline):
    model = Translation
    readonly_fields = ('verbose_lang_code', 'updated',)
    fields = [('verbose_lang_code', 'translation'), ]# 'updated')]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for l in avaiable_languages_without_default():
            if not request.user.has_perm("dbtrans.can_translate_to_%s" % (l[0])):
                qs = qs.exclude(lang_code=l[0])
        return qs

    def verbose_lang_code(self, obj):
        return get_verbose_language(obj.lang_code)
    verbose_lang_code.short_description = _(u'Language')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TranslateFieldAdmin(admin.ModelAdmin):
    list_display = ['original', 'field', 'changed',]
    list_filter = [GenericRelationsRelatedOnlyInSelf, 'field']
    inlines = [TranslationInline, ]
    fields = [
        ('ct', 'field', 'changed'),
        ('original',)
    ]

    readonly_fields = ['ct', 'field', 'changed', 'original']

    def get_model_perms(self, request):
        return {
            'add': False,
            'change': self.has_change_permission(request),
            'delete': False,
        }

admin.site.register(TranslatedField, TranslateFieldAdmin)


class TranslationAdmin(admin.ModelAdmin):
    form = TranslationAdminForm
    list_display = ['original', 'language', 'translation', 'updated']
    # fields = ['language', 'translation', 'updated','original', ]
    readonly_fields = ['updated', 'original', ]
    list_filter = [GenericRelationsRelatedOnly, AvaiableLanguages, 'field__field', EmptyFields, FuzzyOnly]
    list_editable = ['translation',]
    actions = ['update_translations_codes', ]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(TranslationAdmin, self).get_queryset(request)
        for l in avaiable_languages_without_default():
            if not request.user.has_perm("dbtrans.can_translate_to_%s" % (l[0])):
                qs = qs.exclude(lang_code=l[0])
        return qs

    def save_model(self, request, obj, form, change):
        obj.updated = True
        super().save_model(request, obj, form, change)

    def update_translations_codes(self, request, queryset):
        for o in queryset:
            o.field.add_new_translation()
    update_translations_codes.short_description = _(u'Update new language')

    def language(self, obj):
        from .functions import get_verbose_language
        return get_verbose_language(obj.lang_code)

    def original(self, obj):
        return obj.original()

    def get_model_perms(self, request):
        return {
            'add': False,
            'change': self.has_change_permission(request),
            'delete': False,
        }


admin.site.register(Translation, TranslationAdmin)