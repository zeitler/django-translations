from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class EmptyFields(SimpleListFilter):
    title = _('Empty')
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return [
            ('e', _('Empty fields only')),
        ]

    def queryset(self, request, queryset):
        return queryset.filter(translation="") if self.value() else queryset


class FuzzyOnly(SimpleListFilter):
    title = _('Fuzzy')
    parameter_name = 'fuzzy'

    def lookups(self, request, model_admin):
        return [('f', _('Fuzzy fields only')), ]

    def queryset(self, request, queryset):
        return queryset.filter(updated=True) if self.value() else queryset


