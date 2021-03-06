from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^loginout$', views.do_logout, name='logout'),
    url(r'^register/(?P<reset>[0-1])$', views.register, name='register'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^password/(?P<type>[0-9])/(?P<email>[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+)$', views.password, name='password'),
    url(r'checkpsw$', views.checkpsw, name='checkpsw'),
    url(r'^checklogin$', views.checklogin, name='checklogin'),
    url(r'^home$', views.home, name='home'),
    url(r'^upload$', views.upload_file, name='upload'),
    url(r'^home/(?P<section>[0-9])$', views.selected_section, name='selected_section'),
    url(r'^wxappsender$', views.wxapp_sender, name='wxapp_sender')
    # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]