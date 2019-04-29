from django.urls import path
from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='index_view'),
    path('products', ProductListView.as_view(), name='product_listview'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detailview'),
    path('categorys', CategoryListView.as_view(), name='category_listview'),
    path('categorys/<int:pk>/', CategoryDetailView.as_view(), name='category_detailview'),
]
