from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.home),
    url(r'^home/$', views.home, name="home"),
    url(r'^logout/$', views.logout_user, name="logout"),
    url(r'^sign/$', views.sign, name="sign"),
    url(r'^list/$', views.list, name="list"),
    url(r'^detail/(?P<id>\d+)/$', views.detail, name="detail"),
]