from django import forms
from django.contrib.auth.models import User
from .models import Gallery_Image, Profile, Affiliation, Dataset, Data, Partner, Event
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from datetimewidget.widgets import DateTimeWidget, DateWidget

class UserEditForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(UserEditForm, self).__init__(*args, **kwargs)
		self.fields['username'].required = True
		self.fields['email'].required = True

	class Meta:
		model = User
		fields = [
			"username",
			"email"
		]
		widgets = {
			'username': forms.TextInput(attrs={'class': "form-control"}),
			'email': forms.EmailInput(attrs={'class': "form-control"}),
		}

	def clean(self):
		return self.cleaned_data

class MemberSelectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		qset = kwargs.pop('qset', Profile.objects.all())
		super(MemberSelectForm, self).__init__(*args, **kwargs)
		self.fields['email'] = forms.ModelMultipleChoiceField(required=True, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset)

	def clean(self):
		return self.cleaned_data

class PartnerSelectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		qset = kwargs.pop('qset', Partner.objects.all())
		super(PartnerSelectForm, self).__init__(*args, **kwargs)
		self.fields['partner'] = forms.ModelMultipleChoiceField(required=True, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset)

	def clean(self):
		return self.cleaned_data

class ProfileForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(ProfileForm, self).__init__(*args, **kwargs)
		self.fields['bio'].required = False
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True

	class Meta:
		model = Profile
		fields = [
			"bio",
			"first_name",
			"last_name",
		]
		widgets = {
			'bio': forms.Textarea(attrs={'class': "form-control"}),
			'first_name': forms.TextInput(attrs={'class': "form-control"}),
			'last_name': forms.TextInput(attrs={'class': "form-control"}),
		}

	def clean(self):
		return self.cleaned_data

class AffiliationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AffiliationForm, self).__init__(*args, **kwargs)
		self.fields['name'].required = False
		self.fields['country'].required = False
		self.fields['city'].required = False

	class Meta:
		model = Affiliation
		fields = [
			"name",
			"country",
			"city"
		]
		widgets = {
			'name': forms.TextInput(attrs={'class': "form-control"}),
			'country': forms.TextInput(attrs={'class': "form-control"}),
			'city': forms.TextInput(attrs={'class': "form-control"}),
		}

class UserLogForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(UserLogForm, self).__init__(*args, **kwargs)
		self.fields['username'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['password'] = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class SelectRoleForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(SelectRoleForm, self).__init__(*args, **kwargs)
		self.fields['role_select'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True)
		self.fields['role_select'].choices = choices

	role_select = forms.ChoiceField(choices=(), required=True)

	def clean(self):
		return self.cleaned_data	

class RoleCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(RoleCreationForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class TrackCreationForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(TrackCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget())
		self.fields['metrics'] = forms.CharField(required=False, widget=CKEditorWidget())
		self.fields['baseline'] = forms.CharField(required=False, widget=CKEditorWidget())
		self.fields['dataset_select'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices)

	def clean(self):
		return self.cleaned_data

class TrackEditForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		track = kwargs.pop('track', None)
		super(TrackEditForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=track.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=track.description)
		self.fields['metrics'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=track.metrics)
		self.fields['baseline'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=track.baseline)
		self.fields['dataset_select'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices, initial=track.dataset.id)

	def clean(self):
		return self.cleaned_data
		
class GalleryImageForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(GalleryImageForm, self).__init__(*args, **kwargs)
		self.fields['f_id'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class GalleryImageEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		image = kwargs.pop('image', None)
		super(GalleryImageEditForm, self).__init__(*args, **kwargs)
		if image:
			self.fields['desc'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=image.description)

	def clean(self):
		return self.cleaned_data

class MemberCreationForm(RegistrationForm):
	def __init__(self, *args, **kwargs):
		super(MemberCreationForm, self).__init__(*args, **kwargs)
		self.fields['username'] = forms.CharField(required=True, initial='zyx')
		self.fields['first_name'] = forms.CharField(required=True, initial='zyx')
		self.fields['last_name'] = forms.CharField(required=True, initial='zyx')
		self.fields['email'] = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}))
		self.fields['password1'] = forms.CharField(required=True, initial='a1234567')
		self.fields['password2'] = forms.CharField(required=True, initial='a1234567')

	def clean(self):
		username = self.cleaned_data.get('email').split("@")[0]
		if username:
			if User.objects.filter(username=username).exists():
				raise forms.ValidationError('This email is not unique.')
		return self.cleaned_data

class UserRegisterForm(RegistrationForm):
	def __init__(self, *args, **kwargs):
		super(UserRegisterForm, self).__init__(*args, **kwargs)
		self.fields['username'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['email'] = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}))
		self.fields['password1'] = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
		self.fields['password2'] = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
		self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}))
		self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}))
		self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['newsletter'] = forms.BooleanField(required=True, initial=True)

	def clean(self):
		username = self.cleaned_data.get('username')
		email = self.cleaned_data.get('email')
		if email:
			if User.objects.filter(email=email).exists():
				raise forms.ValidationError('Your email is not unique.')
		if username:
			if User.objects.filter(username=username).exists():
				raise forms.ValidationError('Your usrename is not unique.')
		return self.cleaned_data

class EditProfileForm(forms.Form):
	def __init__(self, *args, **kwargs):
		profile = kwargs.pop('profile', None)
		user = kwargs.pop('user', None)
		affiliation = kwargs.pop('affiliation', None)
		super(EditProfileForm, self).__init__(*args, **kwargs)
		if affiliation == None:
			self.fields['username'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=user.username)
			self.fields['email'] = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}), initial=user.email)
			self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}))
			self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}))
			self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['newsletter'] = forms.BooleanField(required=False, initial=True)
		else:
			self.fields['username'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=user.username)
			self.fields['email'] = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}), initial=user.email)
			self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.first_name)
			self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.last_name)
			self.fields['staff'] = forms.TypedChoiceField(required=False, choices=((False, 'False'), (True, 'True')), widget=forms.RadioSelect, initial=user.is_staff)
			self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}), initial=profile.avatar)
			self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}), initial=profile.bio)
			self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.name)
			self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.country)
			self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.city)
			self.fields['newsletter'] = forms.BooleanField(required=False, initial=profile.newsletter)

	def clean(self):
		return self.cleaned_data

class EditExtraForm(forms.Form):
	def __init__(self, *args, **kwargs):
		profile = kwargs.pop('profile', None)
		affiliation = kwargs.pop('affiliation', None)
		super(EditExtraForm, self).__init__(*args, **kwargs)
		if profile == None and affiliation == None:
			self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}))
			self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}))
			self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['email'] = forms.CharField(required=False, widget=forms.EmailInput(attrs={'class': "form-control"}))
			self.fields['main_org'] = forms.TypedChoiceField(required=False, choices=((False, 'False'), (True, 'True')), widget=forms.RadioSelect, initial='False')
		else:
			self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.first_name)
			self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.last_name)
			self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}), initial=profile.avatar)
			self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}), initial=profile.bio)
			self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.name)
			self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.country)
			self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.city)
			self.fields['email'] = forms.CharField(required=False, widget=forms.EmailInput(attrs={'class': "form-control"}), initial=profile.email)
			self.fields['main_org'] = forms.TypedChoiceField(required=False, choices=((False, 'False'), (True, 'True')), widget=forms.RadioSelect, initial=profile.main_org)
			if profile.user:
				self.fields['newsletter'] = forms.BooleanField(required=False, initial=profile.newsletter)

	def clean(self):
		return self.cleaned_data

class UserLoginForm(AuthenticationForm):
	username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
	password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))

class ChangePassForm(PasswordChangeForm):
	old_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
	new_password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
	new_password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))

class ResetPassForm(PasswordResetForm):
	email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}))

	def clean(self):	
		email = self.cleaned_data.get('email')
		if email:
			if User.objects.filter(email=email).exists():
				return self.cleaned_data
			else:
				raise forms.ValidationError('This email is not registered.')
		

class SetPassForm(SetPasswordForm):
	new_password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
	new_password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))

class DatasetCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(DatasetCreationForm, self).__init__(*args, **kwargs)
		self.fields['dataset_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget())
		self.fields['evaluation_file'] = forms.FileField(required=False)
		self.fields['gt_file'] = forms.FileField(required=False)
		self.fields['threshold'] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': "form-control"}))
		self.fields['threshold_extra'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=[('1','<'),('2','>')])

	def clean(self):
		return self.cleaned_data

class DatasetEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		dataset = kwargs.pop('dataset', None)
		super(DatasetEditForm, self).__init__(*args, **kwargs)
		self.fields['dataset_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=dataset.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=dataset.description)
		if dataset.evaluation_file:
			self.fields['evaluation_file'] = forms.FileField(required=False, initial=dataset.evaluation_file)
		else:
			self.fields['evaluation_file'] = forms.FileField(required=False)
		if dataset.gt_file:
			self.fields['gt_file'] = forms.FileField(required=False, initial=dataset.gt_file)
		else:
			self.fields['gt_file'] = forms.FileField(required=False)
		if dataset.threshold:
			if dataset.threshold < 0:
				self.fields['threshold'] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': "form-control"}), initial=-dataset.threshold)
			else:
				self.fields['threshold'] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': "form-control"}), initial=dataset.threshold)
			self.fields['threshold_extra'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=[('1','<'),('2','>')])
		else:
			self.fields['threshold'] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': "form-control"}))
			self.fields['threshold_extra'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=[('1','<'),('2','>')])

	def clean(self):
		return self.cleaned_data

class DataCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(DataCreationForm, self).__init__(*args, **kwargs)
		self.fields['data_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['data_desc'] = forms.CharField(required=True, widget=CKEditorWidget())
		self.fields['data_software'] = forms.CharField(required=False, widget=CKEditorWidget())
		self.fields['data_metric'] = forms.CharField(required=False, widget=CKEditorWidget())

	def clean(self):
		return self.cleaned_data

class DataEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		data = kwargs.pop('data', None)
		super(DataEditForm, self).__init__(*args, **kwargs)
		self.fields['data_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=data.title)
		self.fields['data_desc'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=data.description)
		self.fields['data_software'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=data.software)
		self.fields['data_metric'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=data.metric)

	def clean(self):
		return self.cleaned_data

class FileCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(FileCreationForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['url'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		# self.fields['f_id'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['file'] = forms.FileField(required=False)

	def clean(self):
		cleaned_data = super(FileCreationForm, self).clean()
		url = cleaned_data.get("url")
		file = cleaned_data.get("file")
		if not url and not file:
			raise forms.ValidationError("Please enter an URL or upload a file.")
		return self.cleaned_data

class EventCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(EventCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget())
		self.fields['event_type'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=[('1','Challenge'),('2','Special Issue'),('3', 'Workshop')])

	def clean(self):
		return self.cleaned_data

class EditEventForm(forms.Form):
	def __init__(self, *args, **kwargs):
		event = kwargs.pop('event', None)
		super(EditEventForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=event.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=event.description)
		# self.fields['file'] = forms.FileField(required=False)

	def clean(self):
		return self.cleaned_data

class EditChallengeResult(forms.Form):
	def __init__(self, *args, **kwargs):
		super(EditChallengeResult, self).__init__(*args, **kwargs)
		self.fields['file'] = forms.FileField(required=False)

	def clean(self):
		return self.cleaned_data

class ChallengeEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		event = kwargs.pop('event', None)
		super(EditEventForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=event.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=event.description)

	def clean(self):
		return self.cleaned_data

class NewsCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(NewsCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget())

	def clean(self):
		return self.cleaned_data

class NewsEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		news = kwargs.pop('news', None)
		super(NewsEditForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=news.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=news.description)

	def clean(self):
		return self.cleaned_data

class SelectDatasetForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(SelectDatasetForm, self).__init__(*args, **kwargs)
		self.fields['select_dataset'] = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple(), choices=choices)

	def clean(self):
		return self.cleaned_data

class PartnerCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(PartnerCreationForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['url'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['banner'] = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': "form-control"}))
		self.fields['first_name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['last_name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['email'] = forms.CharField(required=False, widget=forms.EmailInput(attrs={'class': "form-control"}))
		self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class ProgramCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ProgramCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget())
		self.fields['time'] = forms.DateTimeField(required=True, widget=DateTimeWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy hh:ii'}), input_formats=['%m/%d/%Y %H:%M'])

	def clean(self):
		return self.cleaned_data

class ScheduleCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ScheduleCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget())
		self.fields['time'] = forms.DateField(required=True, widget=DateWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy'}), input_formats=['%m/%d/%Y'])

	def clean(self):
		return self.cleaned_data

class ScheduleEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		schedule = kwargs.pop('schedule', None)
		super(ScheduleEditForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=schedule.title)
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget(), initial=schedule.description)
		self.fields['time'] = forms.DateField(required=True, widget=DateWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy'}), input_formats=['%m/%d/%Y'], initial=schedule.date)

	def clean(self):
		return self.cleaned_data

class ProgramEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		schedule = kwargs.pop('schedule', None)
		super(ProgramEditForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=schedule.title)
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget(), initial=schedule.description)
		self.fields['time'] = forms.DateTimeField(required=True, widget=DateTimeWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy hh:ii'}), input_formats=['%m/%d/%Y %H:%M'], initial=schedule.date)

	def clean(self):
		return self.cleaned_data

class RelationCreationForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(RelationCreationForm, self).__init__(*args, **kwargs)
		self.fields['event'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices)
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget())

	def clean(self):
		return self.cleaned_data

class RelationEditForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		relation = kwargs.pop('relation', None)
		super(RelationEditForm, self).__init__(*args, **kwargs)
		if relation.challenge_relation:
			self.fields['event'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices, initial=relation.challenge_relation.id)
		elif relation.issue_relation:
			self.fields['event'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices, initial=relation.issue_relation.id)
		elif relation.workshop_relation:
			self.fields['event'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices, initial=relation.workshop_relation.id)
		elif relation.dataset_relation:
			self.fields['event'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True, choices=choices, initial=relation.dataset_relation.id)
		self.fields['description'] = forms.CharField(required=False, widget=CKEditorUploadingWidget(), initial=relation)

	def clean(self):
		return self.cleaned_data

class SubmissionCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SubmissionCreationForm, self).__init__(*args, **kwargs)
		self.fields['prediction_file'] = forms.FileField(required=True)

	def clean(self):
		return self.cleaned_data

class SubmissionInstructionsForm(forms.Form):
	def __init__(self, *args, **kwargs):
		result_grid = kwargs.pop('result_grid', None)
		super(SubmissionInstructionsForm, self).__init__(*args, **kwargs)
		if result_grid:
			self.fields['text'] = forms.CharField(required=False, widget=CKEditorUploadingWidget(), initial=result_grid.instructions)
		else:
			self.fields['text'] = forms.CharField(required=False, widget=CKEditorUploadingWidget())

	def clean(self):
		return self.cleaned_data

class SubmissionScoresForm(forms.Form):
	def __init__(self, *args, **kwargs):
		headers = kwargs.pop('headers', None)
		super(SubmissionScoresForm, self).__init__(*args, **kwargs)
		for h in headers:
			self.fields[h.name] = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class ResultRowForm(forms.Form):
	def __init__(self, *args, **kwargs):
		headers = kwargs.pop('headers', None)
		super(ResultRowForm, self).__init__(*args, **kwargs)
		self.fields['username'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		for h in headers:
			self.fields[h.name] = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class ResultRowEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		scores = kwargs.pop('scores', None)
		super(ResultRowEditForm, self).__init__(*args, **kwargs)
		for s in scores:
			self.fields[s.name] = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'class': "form-control"}), initial=s.score)

	def clean(self):
		return self.cleaned_data

# class ResultUserEditForm(forms.Form):
# 	def __init__(self, *args, **kwargs):
# 		result_user = kwargs.pop('result_user', None)
# 		super(ResultUserEditForm, self).__init__(*args, **kwargs)
# 		if result_user:
# 			for r in result_user:
# 				self.fields[r.name] = forms.URLField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=r.content)

# 	def clean(self):
# 		return self.cleaned_data

class ResultUserForm(forms.Form):
	def __init__(self, *args, **kwargs):
		result_user = kwargs.pop('result_user', None)
		super(ResultUserForm, self).__init__(*args, **kwargs)
		if result_user:
			self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=result_user.name)
			if result_user.content:
				self.fields['content'] = forms.CharField(required=False, widget=CKEditorWidget(), initial=result_user.content)
			else:
				self.fields['content'] = forms.CharField(required=False, widget=CKEditorWidget())
			if result_user.paper:
				self.fields['paper'] = forms.FileField(required=False, initial=result_user.paper)
			else:
				self.fields['paper'] = forms.FileField(required=False)
		else:
			self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['content'] = forms.CharField(required=False, widget=CKEditorWidget())
			self.fields['paper'] = forms.FileField(required=False)

	def clean(self):
		cleaned_data = super(ResultUserForm, self).clean()
		content = cleaned_data.get("content")
		paper = cleaned_data.get("paper")
		if not content and not paper:
			raise forms.ValidationError("Please enter text or upload a file.")
		return self.cleaned_data

class ColEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		col = kwargs.pop('col', None)
		super(ColEditForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=col.name)

	def clean(self):
		return self.cleaned_data

class HeaderEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		header = kwargs.pop('header', None)
		super(HeaderEditForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=header.name)

	def clean(self):
		return self.cleaned_data

class SubmissionEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		submission = kwargs.pop('submission', None)
		super(SubmissionEditForm, self).__init__(*args, **kwargs)
		if submission and submission.source_code:
			self.fields['source_code'] = forms.URLField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=submission.source_code)
		else:
			self.fields['source_code'] = forms.URLField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		if submission and submission.publication:
			self.fields['publication'] = forms.URLField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=submission.publication)
		else:
			self.fields['publication'] = forms.URLField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		if submission and submission.publication:
			self.fields['sub_file'] = forms.FileField(required=False, initial=submission.sub_file)
		else:
			self.fields['sub_file'] = forms.FileField(required=False)

	def clean(self):
		return self.cleaned_data

class PublicationCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		qset1 = kwargs.pop('qset1', Event.objects.all())
		qset2 = kwargs.pop('qset2', Dataset.objects.all())
		super(PublicationCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget())
		# self.fields['url'] = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "URL"}))
		self.fields['event'] = forms.ModelMultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset1)
		self.fields['dataset'] = forms.ModelMultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset2)

	def clean(self):
		return self.cleaned_data

class PublicationEventCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(PublicationEventCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget())
		# self.fields['url'] = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "URL"}))

	def clean(self):
		return self.cleaned_data

class PublicationEditForm(forms.Form):
	def __init__(self, publication, *args, **kwargs):
		super(PublicationEditForm, self).__init__(*args, **kwargs)
		if publication.title:
			self.fields['title'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=publication.title)
		else:
			self.fields['title'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=publication.content)
		# self.fields['url'] = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': "URL"}), initial=publication.url)

	def clean(self):
		return self.cleaned_data

class ResultNewTableForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ResultNewTableForm, self).__init__(*args, **kwargs)
		self.fields['cols'] = forms.IntegerField(required=True, min_value=1, max_value=10, widget=forms.TextInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class EditHomeForm(forms.Form):
	def __init__(self, *args, **kwargs):
		chalearn = kwargs.pop('chalearn', None)
		super(EditHomeForm, self).__init__(*args, **kwargs)
		self.fields['text'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=chalearn.home_text)

	def clean(self):
		return self.cleaned_data

class EditHelpForm(forms.Form):
	def __init__(self, *args, **kwargs):
		help = kwargs.pop('help', None)
		super(EditHelpForm, self).__init__(*args, **kwargs)
		self.fields['text'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=help.help_text)

	def clean(self):
		return self.cleaned_data

class CIMLBookForm(forms.Form):
	def __init__(self, *args, **kwargs):
		book = kwargs.pop('book', None)
		super(CIMLBookForm, self).__init__(*args, **kwargs)
		if book:
			self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=book.name)
			self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=book.content)
		else:
			self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
			self.fields['content'] = forms.CharField(required=True, widget=CKEditorWidget())

	def clean(self):
		return self.cleaned_data