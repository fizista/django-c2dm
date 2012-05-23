from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'registration$', 'django_c2dm.views.set_registration_id'),
)

