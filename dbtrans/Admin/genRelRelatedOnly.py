from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from dbtrans.models import TranslatedField
from django.contrib.contenttypes.models import ContentType


class GenericRelationsRelatedOnly(SimpleListFilter):
    title = _('Modelo')
    parameter_name = 'model'

    def lookups(self, request, model_admin):
        cts = []
        for x in TranslatedField.objects.all().values('ct').distinct():
            for k, v in x.items():
                ct = ContentType.objects.get_for_id(v)
                cts.append((v, ct.model_class()._meta.verbose_name))
        return cts

    def queryset(self, request, queryset):
        return queryset.filter(field__ct=self.value()) if self.value() else queryset


class GenericRelationsRelatedOnlyInSelf(GenericRelationsRelatedOnly):
    def queryset(self, request, queryset):
        return queryset.filter(ct=self.value()) if self.value() else queryset