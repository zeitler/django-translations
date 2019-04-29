from django.db import models
from dbtrans.decorator import Translate
from django.utils.translation import ugettext as _
from django.urls import reverse


@Translate('name', 'observations')
class Category(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('Name'))
    observations = models.TextField(max_length=200, verbose_name=_('Observations'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categorys')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detailview", args=(self.id,))


@Translate('name')
class Product(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('Name'))
    description = models.TextField(max_length=200, verbose_name=_('Description'))
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name=_('Price'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detailview", args=(self.id,))