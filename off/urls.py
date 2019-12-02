from django.conf.urls import url
from . import views

app_name = 'off'

urlpatterns = [

    url(r'^article/(?P<search>[\w\.\'\&%\s]+)/$', views.article, name='article'),
    url(r'^deconnexion/$', views.log_out, name='logout'),
    url(r'^inscription/$', views.login_registration, name='registration'),
    url(r'^compte/$', views.account, name='account'),
    url(r'^produit/(?P<product_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^mesproduits/$', views.my_products, name='my_products'),
    url(r'^mentions/$', views.mentions, name='mentions'),
]
