from django.conf.urls import url, include
from .views import *

app_name = 'reception'
urlpatterns = [
    url(r'^$', WelcomeView.as_view(), name='welcome'),
    url(r'^event/$', EventWelcomeView.as_view(), name='event'),
    url(r'^sign-in/$', sign_in, name='sign_in')
]