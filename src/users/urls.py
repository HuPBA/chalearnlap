from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserRegisterForm, UserLoginForm, ChangePassForm, ResetPassForm, SetPassForm, MemberCreationForm
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
    url(r'^profile/creation/$', views.Backend.as_view(form_class = MemberCreationForm,template_name='registration/registration_form_email.html'), name="profile_creation"),
    url(r'^profile/select/(?P<id>\d+)/$', views.profile_select, name="profile_select"),
    # Dataset urls
    url(r'^dataset/list/$', views.dataset_list, name="dataset_list"),
    url(r'^dataset/creation/$', views.dataset_creation, name="dataset_creation"),
    url(r'^dataset/edit/(?P<id>\d+)/$', views.dataset_edit, name="dataset_edit"),
    url(r'^dataset/(?P<id>\d+)/information/$', views.dataset_info, name="dataset_info"),
    url(r'^dataset/(?P<id>\d+)/source/$', views.dataset_source, name="dataset_source"),
    url(r'^dataset/(?P<id>\d+)/remove/$', views.dataset_remove, name="dataset_remove"),
    # url(r'^dataset/select/(?P<id>\d+)/$', views.dataset_select, name="dataset_select"),
    # Data urls
    url(r'^dataset/(?P<id>\d+)/data/creation/$', views.data_creation, name="data_creation"),
    url(r'^dataset/(?P<dataset_id>\d+)/data/(?P<id>\d+)/remove/$', views.data_remove, name="data_remove"),
    url(r'^dataset/(?P<dataset_id>\d+)/data/(?P<id>\d+)/information/$', views.data_info, name="data_info"),
    url(r'^dataset/(?P<dataset_id>\d+)/data/(?P<id>\d+)/edit/$', views.data_edit, name="data_edit"),
    url(r'^dataset/(?P<dataset_id>\d+)/data/(?P<id>\d+)/file/creation/$', views.file_creation, name="file_creation"),
    url(r'^dataset/(?P<dataset_id>\d+)/data/(?P<id>\d+)/file/(?P<file_id>\d+)/remove/$', views.file_remove, name="file_remove"),
    # Partner urls
    url(r'^partner/list/$', views.partner_list, name="partners_list"),
    url(r'^partner/creation/$', views.partner_creation, name="partner_creation"),
    url(r'^partner/select/(?P<id>\d+)/$', views.partner_select, name="partner_select"),
    # Event urls (Challenge, Workshops...)
    url(r'^event/list/$', views.event_list, name="event_list"),
    url(r'^event/creation/$', views.event_creation, name="event_creation"),
    url(r'^event/(?P<id>\d+)/remove/$', views.event_remove, name="event_remove"),
    url(r'^event/(?P<id>\d+)/member/(?P<member_id>\d+)/remove$', views.event_member_remove, name="event_member_remove"),
    url(r'^event/(?P<id>\d+)/news/(?P<news_id>\d+)/remove$', views.event_news_remove, name="event_news_remove"),
    url(r'^event/(?P<id>\d+)/program/(?P<program_id>\d+)/remove$', views.event_program_remove, name="event_program_remove"),
    url(r'^event/(?P<id>\d+)/partner/(?P<partner_id>\d+)/remove$', views.event_partner_remove, name="event_partner_remove"),
    url(r'^event/(?P<id>\d+)/news/creation/$', views.news_creation, name="news_creation"),
    url(r'^event/(?P<id>\d+)/news/edit/$', views.news_edit, name="news_edit"),
    url(r'^event/(?P<id>\d+)/program/creation/$', views.program_creation, name="program_creation"),
    url(r'^event/(?P<id>\d+)/program/(?P<program_id>\d+)/edit/$', views.program_edit, name="program_edit"),
    url(r'^event/(?P<event_id>\d+)/program/(?P<program_id>\d+)/subevent/creation/$', views.subevent_creation, name="subevent_creation"),
    # url(r'^event/edit/(?P<id>\d+)/$', views.event_edit, name="event_edit"),
    url(r'^event/proposal/$', views.event_proposal, name="event_proposal"),
    url(r'^challenge/(?P<id>\d+)/edit/$', views.challenge_edit, name="challenge_edit"),
    url(r'^challenge/(?P<id>\d+)/information/$', views.challenge_info, name="challenge_info"),
    url(r'^challenge/(?P<id>\d+)/members/$', views.challenge_members, name="challenge_members"),
    url(r'^challenge/(?P<id>\d+)/sponsors/$', views.challenge_sponsors, name="challenge_sponsors"),
    url(r'^challenge/(?P<id>\d+)/result/$', views.challenge_result, name="challenge_result"),
    url(r'^challenge/(?P<id>\d+)/program/$', views.challenge_program, name="challenge_program"),
    url(r'^challenge/(?P<id>\d+)/track/(?P<track_id>\d+)/remove$', views.track_remove, name="track_remove"),
    url(r'^challenge/(?P<id>\d+)/track/(?P<track_id>\d+)/edit$', views.track_edit, name="track_edit"),
    url(r'^challenge/(?P<id>\d+)/track/(?P<track_id>\d+)/info/$', views.track_info, name="track_info"),
    url(r'^challenge/(?P<id>\d+)/track/creation/$', views.track_creation, name="track_creation"),
    url(r'^workshop/(?P<id>\d+)/edit/$', views.workshop_edit, name="workshop_edit"),
    url(r'^workshop/(?P<id>\d+)/information/$', views.workshop_info, name="workshop_info"),
    url(r'^workshop/(?P<id>\d+)/program/$', views.workshop_program, name="workshop_program"),
    url(r'^workshop/(?P<id>\d+)/speakers/$', views.workshop_speakers, name="workshop_speakers"),
    url(r'^workshop/(?P<id>\d+)/gallery/$', views.workshop_gallery, name="workshop_gallery"),
    url(r'^workshop/(?P<id>\d+)/gallery/add$', views.add_gallery_picture, name="add_gallery_picture"),
    url(r'^workshop/(?P<id>\d+)/speaker/creation$', views.speaker_creation, name="speaker_creation"),
    url(r'^workshop/(?P<id>\d+)/speaker/select$', views.speaker_select, name="speaker_select"),
    url(r'^specialissue/(?P<id>\d+)/edit/$', views.special_issue_edit, name="special_issue_edit"),
    url(r'^specialissue/(?P<id>\d+)/information/$', views.special_issue_info, name="special_issue_info"),
    url(r'^specialissue/(?P<id>\d+)/members/$', views.special_issue_members, name="special_issue_members"),
    # Role urls
    url(r'^role/creation/$', views.role_creation, name="role_creation"),
    # Schedule event urls
    # url(r'^schedule/creation/(?P<id>\d+)/$', views.schedule_creation, name="schedule_creation"),
    # url(r'^schedule/creation/(?P<workshop_id>\d+)/(?P<event_id>\d+)/subevent$', views.subevent_creation, name="subevent_creation"),
    # url(r'^schedule/edit/(?P<id>\d+)/$', views.schedule_edit, name="schedule_edit"),
]