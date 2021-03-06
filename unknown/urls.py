from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^authCode', views.authCode, name='authCode'),
    url(r'^register', views.register, name='register'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^userInfo', views.userInfo, name='userInfo'),
    url(r'upload', views.upload, name='upload'),
    url(r'homeBgImg', views.homeBgImg, name='homeBgImg'),
    url(r'searchTags', views.searchTags, name='searchTags'),
    url(r'popularSearches', views.popularSearches, name='popularSearches'),
    url(r'photos', views.photos, name='photos'),
    url(r'discover', views.discover, name='discover'),
    url(r'leaderboard', views.leaderboard, name='leaderboard'),
    url(r'image', views.image, name='image'),
    url(r'userPhotos', views.userPhotos, name='userPhotos'),
    url(r'doThumbup', views.doThumbup, name='doThumbup'),
    url(r'deletePhoto', views.deletePhoto, name='deletePhoto'),
    url(r'blocked', views.blocked, name='blocked'),
    url(r'getBlockedList', views.getBlockedList, name='getBlockedList'),
    url(r'report', views.report, name='report'),
]