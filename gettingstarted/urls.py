from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include('polls.urls', namespace="polls")),
    # url(r'^', include('ipa.urls', namespace='ipa')),
    url(r'^', include('unknown.urls', namespace='unknown')),
    url(r'^porn/', include('porn.urls', namespace='porn')),
    url(r'^unknown/', include('unknown.urls', namespace='unknown'))
]
