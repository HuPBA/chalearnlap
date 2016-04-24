from django import forms
from django.contrib.auth.models import User
from .models import Profile, Affiliation, Dataset, Data
from registration.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

class UserRegForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(UserRegForm, self).__init__(*args, **kwargs)
		self.fields['username'].required = True
		self.fields['password'].required = True
		self.fields['email'].required = True

	confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control"}), required=True)

	class Meta:
		model = User
		fields = [
			"username",
			"password",
			"email"
		]
		widgets = {
			'username': forms.TextInput(attrs={'class': "form-control"}),
			'password': forms.PasswordInput(attrs={'class': "form-control"}),
			'email': forms.EmailInput(attrs={'class': "form-control"}),
		}

	def clean(self):
		password1 = self.cleaned_data.get('password')
		password2 = self.cleaned_data.get('confirm_password')
		print password1
		print password2
		if password1 != password2:
			raise forms.ValidationError(("Passwords don't match"), code='passwords_not_match')
		return self.cleaned_data	

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

class UserCreationForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(UserCreationForm, self).__init__(*args, **kwargs)
		self.fields['event_select'] = forms.ChoiceField(widget=forms.Select(attrs={'class': "form-control"}), required=True)
		self.fields['event_select'].choices = choices

	event_select = forms.ChoiceField(choices=(), required=True)

	def clean(self):
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
		return self.cleaned_data

class EditProfileForm(forms.Form):
	def __init__(self, *args, **kwargs):
		profile = kwargs.pop('profile', None)
		user = kwargs.pop('user', None)
		affiliation = kwargs.pop('affiliation', None)
		super(EditProfileForm, self).__init__(*args, **kwargs)
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

class DatasetCreationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(DatasetCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'].required = True
		self.fields['description'].required = True

	class Meta:
		model = Dataset
		fields = [
			"title",
			"description",
		]
		widgets = {
			'title': forms.TextInput(attrs={'class': "form-control"}),
			'description': forms.Textarea(attrs={'class': "form-control"}),
		}
	def clean(self):
		return self.cleaned_data

class DataCreationForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(DataCreationForm, self).__init__(*args, **kwargs)
		self.fields['title'] = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': "form-control"}))
		self.fields['file'] = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': "form-control"}))

	def clean(self):
		return self.cleaned_data