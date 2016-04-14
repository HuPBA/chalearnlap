from django import forms
from django.contrib.auth.models import User
from .models import Profile, Affiliation

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