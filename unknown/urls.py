from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^authCode', views.authCode, name='authCode'),
    url(r'^register', views.register, name='register'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^userInfo', views.userInfo, name='userInfo'),
    url(r'upload', views.upload, name='upload'),

]