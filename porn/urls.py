from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^pages/$', views.pages, name='pages'),
]