from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserRegisterForm, UserLoginForm, ChangePassForm, ResetPassForm, SetPassForm
from registration.backends.default.views import RegistrationView, ActivationView
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^home/$', views.home, name="home"),
    # Register, Login, edit password urls (Django auth)
    url(r'^register/$', RegistrationView.as_view(form_class = UserRegisterForm), name = 'register'),
    url(r'^login/$', auth_views.login, {'authentication_form': UserLoginForm}, name = 'auth_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='auth_logout'),
    url(r'^password/change/$', auth_views.password_change, {'password_change_form': ChangePassForm}, name='auth_password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, {'password_reset_form': ResetPassForm}, name='auth_password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {'set_password_form': SetPassForm}, name='auth_password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^activate/complete/$', TemplateView.as_view(template_name='registration/activation_complete.html'), name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', ActivationView.as_view(), name='registration_activate'),
    url(r'^register/complete/$', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
    url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'), name='registration_disallowed'),
    # User urls
    url(r'^user/list/$', views.user_list, name="user_list"),
    url(r'^user/edit/(?P<id>\d+)/$', views.user_edit, name="user_edit"),
    # Profile urls (Editors, Organizers...)
    url(r'^profile/edit/(?P<id>\d+)/$', views.profile_edit, name="profile_edit"),
    url(r'^profile/creation/(?P<id>\d+)/$', views.profile_creation, name="profile_creation"),
    # Dataset urls
    url(r'^dataset/list/$', views.dataset_list, name="dataset_list"),
    url(r'^dataset/creation/$', views.dataset_creation, name="dataset_creation"),
    url(r'^dataset/edit/(?P<id>\d+)/$', views.dataset_edit, name="dataset_edit"),
    url(r'^dataset/detail/(?P<id>\d+)/$', views.dataset_detail, name="dataset_detail"),
    url(r'^dataset/select/(?P<id>\d+)/$', views.dataset_select, name="dataset_select"),
    # Data urls
    url(r'^data/creation/(?P<id>\d+)/$', views.data_creation, name="data_creation"),
    url(r'^data/detail/(?P<id>\d+)/(?P<dataset_id>\d+)/$', views.data_detail, name="data_detail"),
    # Partner urls
    url(r'^partner/list/$', views.partner_list, name="partners_list"),
    # Event urls (Challenge, Workshops...)
    url(r'^event/list/$', views.event_list, name="event_list"),
    url(r'^event/creation/$', views.event_creation, name="event_creation"),
    url(r'^event/edit/(?P<id>\d+)/$', views.event_edit, name="event_edit"),
    url(r'^event/detail/(?P<id>\d+)/$', views.event_detail, name="event_detail"),
    # Role urls
    url(r'^role/creation/$', views.role_creation, name="role_creation"),
    # News urls
    url(r'^news/creation/(?P<id>\d+)/$', views.news_creation, name="news_creation"),
    url(r'^news/edit/(?P<id>\d+)/$', views.news_edit, name="news_edit"),
]