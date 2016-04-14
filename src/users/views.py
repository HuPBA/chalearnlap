from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import UserRegForm, UserLogForm, ProfileForm, AffiliationForm, UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Profile_Event, Affiliation, Event

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
	profiles = Profile.objects.all()
	admins = User.objects.all().filter(is_staff=True)
	editors = []
	organizers = []
	for o in Profile_Event.objects.all():
		if o.role == 'editor':
			editors.append(o.profile)
		elif o.role == 'organizer':
			organizers.append(o.profile)
	context = {
		"profiles": profiles,
		"admins": admins,
		"editors": editors,
		"organizers": organizers
	}
	return render(request, "list-users.html", context);

def detail(request, id=None):
	profile = get_object_or_404(Profile, id=id)
	context = {
		"profile": profile
	}
	return render(request, "detail.html", context)

@csrf_protect
def user_creation(request, id=None):
	choices = []
	events = Event.objects.all()
	for e in events:
	    choices.append((e.id, e.title))
	userCreationForm = UserCreationForm(choices)
	profileForm = ProfileForm()
	affiliationForm = AffiliationForm()
	if id=='1':
		role = "organizer"
	elif id=='2':
		role = "editor"
	if request.method == 'POST':
		userCreationForm = UserCreationForm(choices, request.POST)
		profileForm = ProfileForm(request.POST)
		affiliationForm = AffiliationForm(request.POST)
		if userCreationForm.is_valid():
			if profileForm.is_valid():
				if affiliationForm.is_valid():
					fname = profileForm.cleaned_data["first_name"]
					lname = profileForm.cleaned_data["last_name"]
					bio = profileForm.cleaned_data["bio"]
					aff_name = affiliationForm.cleaned_data["name"]
					aff_country = affiliationForm.cleaned_data["country"]
					aff_city = affiliationForm.cleaned_data["city"]
					event_selected = Event.objects.get(pk=userCreationForm.cleaned_data["event_select"])
					new_aff = Affiliation(name=aff_name, country=aff_country, city=aff_city)
					new_aff.save()
					new_profile = Profile(first_name=fname, last_name= lname, affiliation=new_aff, bio=bio)
					new_profile.save()
					new_profile_event = Profile_Event(profile=new_profile, event=event_selected, role=role)
					new_profile_event.save()
					messages.success(request, "User registered succesfully")
				else:
					messages.error(request, affiliationForm.errors)
			else:
				messages.error(request, profileForm.errors)
		else:
			messages.error(request, userCreationForm.errors)
	context = {
		"userCreationForm": userCreationForm,
		"profileForm": profileForm,
		"affiliationForm": affiliationForm,
		"role": role
	}
	return render(request, "user-creation.html", context)