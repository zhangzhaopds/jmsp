from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^video/$', views.video, name='video'),
    url(r'^categories/$', views.categories, name='categories')
]