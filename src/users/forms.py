from django import forms
from django.contrib.auth.models import User
from .models import Profile, Affiliation, Dataset, Data, Partner
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from datetimewidget.widgets import DateTimeWidget

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
		qset = kwargs.pop('qset', User.objects.all())
		super(MemberSelectForm, self).__init__(*args, **kwargs)
		self.fields['email'] = forms.ModelMultipleChoiceField(required=True, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset)

	def clean(self):
		return self.cleaned_data

class PartnerSelectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		qset = kwargs.pop('qset', Partner.objects.all())
		super(PartnerSelectForm, self).__init__(*args, **kwargs)
		self.fields['partner'] = forms.ModelMultipleChoiceField(required=True, widget=forms.SelectMultiple(attrs={'class': "js-example-basic-multiple", 'id': "input-addmembers"}), queryset=qset)
		self.fields['role'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))

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

	def clean(self):
		username = self.cleaned_data.get('email')
		if username:
			if User.objects.filter(username=username).exists():
				raise forms.ValidationError('Your username is not unique.')
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
		else:
			self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.first_name)
			self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=profile.last_name)
			self.fields['avatar'] = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}), initial=profile.avatar)
			self.fields['bio'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': "form-control"}), initial=profile.bio)
			self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.name)
			self.fields['country'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.country)
			self.fields['city'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control"}), initial=affiliation.city)

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

class SetPassForm(SetPasswordForm):
	new_password1 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))
	new_password2 = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': "form-control"}))

class DatasetCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(DatasetCreationForm, self).__init__(*args, **kwargs)
		self.fields['dataset_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget())

	def clean(self):
		return self.cleaned_data

class DatasetEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		dataset = kwargs.pop('dataset', None)
		super(DatasetEditForm, self).__init__(*args, **kwargs)
		self.fields['dataset_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=dataset.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=dataset.description)

	def clean(self):
		return self.cleaned_data

class DataCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(DataCreationForm, self).__init__(*args, **kwargs)
		self.fields['data_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['data_desc'] = forms.CharField(required=True, widget=CKEditorWidget())

	def clean(self):
		return self.cleaned_data

class DataEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		data = kwargs.pop('data', None)
		super(DataEditForm, self).__init__(*args, **kwargs)
		self.fields['data_title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=data.title)
		self.fields['data_desc'] = forms.CharField(required=True, widget=CKEditorWidget(), initial=data.description)

	def clean(self):
		return self.cleaned_data

class FileCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(FileCreationForm, self).__init__(*args, **kwargs)
		self.fields['name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['file'] = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}))
		self.fields['url'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': "form-control", 'placeholder': 'URL'}))

	def clean(self):
		cleaned_data = super(FileCreationForm, self).clean()
		file = cleaned_data.get("file")
		url = cleaned_data.get("url")
		if not url and not file:
			raise forms.ValidationError("Please, insert a file or a URL")
		else:
			return cleaned_data

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
		self.fields['first_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['last_name'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['email'] = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class': "form-control"}))
		self.fields['bio'] = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data

class ScheduleCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ScheduleCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorUploadingWidget())
		self.fields['time'] = forms.DateTimeField(required=True, widget=DateTimeWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy hh:ii'}), input_formats=['%m/%d/%Y %H:%M'])

	def clean(self):
		return self.cleaned_data

class ScheduleEditForm(forms.Form):
	def __init__(self, *args, **kwargs):
		schedule = kwargs.pop('schedule', None)
		super(ScheduleEditForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}), initial=schedule.title)
		self.fields['description'] = forms.CharField(required=True, widget=CKEditorUploadingWidget(), initial=schedule.description)
		self.fields['time'] = forms.DateTimeField(required=True, widget=DateTimeWidget(bootstrap_version=3, options = {'format': 'mm/dd/yyyy hh:ii'}), input_formats=['%m/%d/%Y %H:%M'], initial=schedule.date)

	def clean(self):
		return self.cleaned_data