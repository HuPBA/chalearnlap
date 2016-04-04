from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import UserRegForm, UserLogForm, ProfileForm, AffiliationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def home(request):
	return render(request, "home.html", {});

def logout_user(request):
	logout(request)
	return render(request, "home.html", {});

@csrf_protect
def sign(request):
	signupForm = UserRegForm()
	signinForm = UserLogForm()
	profileForm = ProfileForm()
	affiliationForm = AffiliationForm()
	if request.method == 'POST':
		if 'signup-button' in request.POST:
			signupForm = UserRegForm(request.POST)
			profileForm = ProfileForm(request.POST)
			affiliationForm = AffiliationForm(request.POST)
			if signupForm.is_valid():
				if profileForm.is_valid():
					if affiliationForm.is_valid():
						new_user = signupForm.save(commit=False)
						new_user.set_password(signupForm.cleaned_data["password"])
						new_user.save()
						new_affiliation = affiliationForm.save()
						new_profile = profileForm.save(commit=False)
						new_profile.user = new_user
						new_profile.affiliation = new_affiliation
						new_profile.save()
						messages.success(request, "User registered succesfully")
					else:
						messages.error(request, affiliationForm.errors)
				else:
					messages.error(request, profileForm.errors)
			else:
				messages.error(request, signupForm.errors)
		if 'signin-button' in request.POST:
			signinForm = UserLogForm(request.POST)
			if signinForm.is_valid():
				username = signinForm.cleaned_data['username']
				password = signinForm.cleaned_data['password']
				user = authenticate(username=username, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
						return render(request, "home.html", {})
					else:
						print 'not active'
				else:
					print 'None'
			else:
				print 'not valid'
				messages.error(request, signinForm.errors)
	context = {
		"signupForm": signupForm,
		"signinForm": signinForm,
		"profileForm": profileForm,
		"affiliationForm": affiliationForm
	}
	return render(request, "sign.html", context)

def list(request):
	queryset = User.objects.all()
	context = {
		"users": queryset,
	}
	return render(request, "list-users.html", context);

def detail(request, id=None):
	instance = get_object_or_404(User, id=id)
	context = {
		"instance": instance
	}
	return render(request, "detail.html", context)