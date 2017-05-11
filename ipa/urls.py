from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^register$', views.register, name='register'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^password/(?P<type>[0-9])/(?P<email>[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+)$', views.password, name='password'),
    url(r'checkpsw$', views.checkpsw, name='checkpsw'),
    url(r'^checklogin$', views.checklogin, name='checklogin'),
    # url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    # url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]