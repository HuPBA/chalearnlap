from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserRegisterForm, UserLoginForm, ChangePassForm, ResetPassForm, SetPassForm
from registration.backends.default.views import RegistrationView, ActivationView
from django.views.generic.base import TemplateView

urlpatterns = [
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

    url(r'^list/$', views.list, name="users-list"),
    url(r'^edit-profile/(?P<id>\d+)/$', views.edit_profile, name="edit-profile"),
    url(r'^edit-extra/(?P<id>\d+)/$', views.edit_extra, name="edit-extra"),
    url(r'^user-creation/(?P<id>\d+)/$', views.user_creation, name="user-creation"),

    url(r'^data-zone/$', views.dataset_list, name="data-zone"),
    url(r'^dataset-creation/$', views.dataset_creation, name="dataset-creation"),
    url(r'^edit-dataset/(?P<id>\d+)/$', views.edit_dataset, name="edit-dataset"),
    url(r'^data-creation/(?P<id>\d+)/$', views.data_creation, name="data-creation"),

    url(r'^partners/$', views.partners_list, name="partners-list"),
]