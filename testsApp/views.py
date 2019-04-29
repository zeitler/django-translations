from django.shortcuts import reverse, redirect
from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.views.generic.base import TemplateView
from django.urls import reverse
from dbtrans.functions import get_avaiable_languages
from .forms import CategoryForm, ProductForm


LANGUAGES = get_avaiable_languages() # SEND TO VIEW ON YOUR OWN WAY. MY SUGGESTION: CONTEXT PROCESSOR...


class IndexView(TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        avaiable_apps = [
            {'url': reverse("product_listview"), 'name': 'Products'},
            {'url': reverse("category_listview"), 'name': 'Categorys'},
        ]
        ctx.update({'avaiable_apps': avaiable_apps, })
        return ctx


class CategoryListView(ListView):
    model = Category
    template_name = 'list.html'
    context_object_name = 'object_list'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'form': CategoryForm(instance=self.get_object())})
        return ctx


class ProductListView(ListView):
    model = Product
    template_name = 'list.html'
    context_object_name = 'object_list'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'detail.html'
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'form': ProductForm(instance=self.get_object())})
        return ctx