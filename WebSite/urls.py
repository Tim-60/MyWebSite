"""
Definition of urls for WebSite.
"""

from datetime import datetime
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from app import views as app_views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('links/', views.links, name='links'),
    path('pool/', views.pool, name='pool'),
    path('registration/', views.registration, name='registration'),
    path('blog', views.blog, name = 'blog'),
    path('blogpost/<int:parametr>/', views.blogpost, name='blogpost'),
    path('summernote/', include('django_summernote.urls')),
    path('newpost/', views.newpost, name = 'newpost'),
    path('video',views.video, name = 'video'),
    path('catalog/', app_views.catalog_view, name='catalog'),
    path('catalog/category/<slug:slug>/', app_views.category_detail, name='category_detail'),
    path('catalog/material/<int:pk>/', app_views.material_detail, name='material_detail'),
    
    path('catalog/admin/', app_views.admin_catalog_dashboard, name='admin_catalog_dashboard'),
    path('catalog/admin/category/add/', app_views.admin_add_category, name='admin_add_category'),
    path('catalog/admin/material/add/', app_views.admin_add_material, name='admin_add_material'),
    path('orders/', app_views.manager_orders, name='manager_orders'),
    path('cart/', app_views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', app_views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', app_views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', app_views.checkout, name='checkout'),
    path('purchases/', app_views.my_orders, name='my_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()