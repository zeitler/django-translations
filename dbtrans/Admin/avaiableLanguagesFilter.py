from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from dbtrans.functions import avaiable_languages_without_default


class AvaiableLanguages(SimpleListFilter):
    """
    Don't return the Default Language
    """
    title = _('Language')
    parameter_name = 'lang'

    def lookups(self, request, model_admin):
        # print(avaiable_languages_without_default())
        return avaiable_languages_without_default()

    def queryset(self, request, queryset):
        return queryset.filter(lang_code=self.value()) if self.value() else queryset
