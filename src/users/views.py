from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse
from .forms import UserRegForm, UserLogForm, ProfileForm, AffiliationForm, UserCreationForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Profile_Event, Affiliation, Event, Dataset, Data, Partner
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext

# from registration.backends.default.views import RegistrationView

# class MyRegistrationView(RegistrationView):
#     def register(self, form):
#         """
#         Implement user-registration logic here.
#         """
#         raise NotImplementedError

def home(request):
	return render(request, "home.html", {});

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def list(request):
	users = User.objects.all().filter(is_staff=False)
	admins = User.objects.all().filter(is_staff=True)
	editors = []
	organizers = []
	for o in Profile_Event.objects.all():
		if o.role == 'editor':
			editors.append(o.profile)
		elif o.role == 'organizer':
			organizers.append(o.profile)
	context = {
		"users": users,
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

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
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

@login_required(login_url='/users/login/')
def edit_profile(request, id=None):
	profile = Profile.objects.filter(user__id=id)[0]
	user = profile.user
	affiliation = profile.affiliation
	form = EditProfileForm(profile=profile, user=user, affiliation=affiliation)
	if request.method == 'POST':
		form = EditProfileForm(request.POST, profile=profile, user=user, affiliation=affiliation)
		if form.is_valid():
			username = form.cleaned_data["username"]
			print username
			first_name = form.cleaned_data["first_name"]
			email = form.cleaned_data["email"]
			last_name = form.cleaned_data["last_name"]
			staff = form.cleaned_data["staff"]
			avatar = form.cleaned_data["avatar"]
			bio = form.cleaned_data["bio"]
			name = form.cleaned_data["name"]
			country = form.cleaned_data["country"]
			city = form.cleaned_data["city"]
			user.username = username
			user.email = email
			user.is_staff = staff
			user.save()
			affiliation.name = name
			affiliation.country = country
			affiliation.city = city
			affiliation.save()
			profile.user = user
			profile.affiliation = affiliation
			profile.first_name = first_name
			profile.last_name = last_name
			profile.avatar = avatar
			profile.bio = bio
			profile.save()
			messages.success(request, "User edited succesfully")
			return render(request, "home.html", {})
		else:
			messages.error(request, form.errors)
	context = {
		"form": form,
		"user_edit": user.id
	}
	return render(request, "edit-profile.html", context)

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def edit_extra(request, id=None):
	profile = Profile.objects.filter(id=id)[0]
	affiliation = profile.affiliation
	form = EditExtraForm(profile=profile, affiliation=affiliation)
	if request.method == 'POST':
		form = EditExtraForm(request.POST, profile=profile, affiliation=affiliation)
		if form.is_valid():
			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["last_name"]
			avatar = form.cleaned_data["avatar"]
			bio = form.cleaned_data["bio"]
			name = form.cleaned_data["name"]
			country = form.cleaned_data["country"]
			city = form.cleaned_data["city"]
			affiliation.name = name
			affiliation.country = country
			affiliation.city = city
			affiliation.save()
			profile.affiliation = affiliation
			profile.first_name = first_name
			profile.last_name = last_name
			profile.avatar = avatar
			profile.bio = bio
			profile.save()
			messages.success(request, "User edited succesfully")
			return render(request, "home.html", {})
		else:
			messages.error(request, form.errors)
	context = {
		"form": form,
	}
	return render(request, "edit-extra.html", context)

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_list(request):
	datasets = Dataset.objects.all()
	context = {
		"datasets": datasets,
	}
	return render(request, "list-dataset.html", context)

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_creation(request):
	datasetform = DatasetCreationForm()
	dataform = DataCreationForm()
	if request.method == 'POST':
		datasetform = DatasetCreationForm(request.POST)
		dataform = DataCreationForm(request.POST, request.FILES)
		if datasetform.is_valid():
			if dataform.is_valid():
				new_dataset = datasetform.save()
				title = dataform.cleaned_data['title']
				file = dataform.cleaned_data['file']
				new_data = Data(title=title, file=file, dataset=new_dataset)
				new_data.save()
				messages.success(request, "Dataset created succesfully")
			else:
				messages.error(request, dataform.errors)
		else:
			messages.error(request, datasetform.errors)
	context = {
		"datasetform": datasetform,
		"dataform": dataform,
	}
	return render(request, "dataset-creation.html", context)

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def edit_dataset(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	context = {
		"dataset": dataset,
		"datas": datas
	}
	return render(request, "edit-dataset.html", context)

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_creation(request, id=None):
	dataform = DataCreationForm()
	if request.method == 'POST':
		dataform = DataCreationForm(request.POST, request.FILES)
		if dataform.is_valid():
			new_dataset = Dataset.objects.filter(id=id)[0]
			title = dataform.cleaned_data['title']
			file = dataform.cleaned_data['file']
			new_data = Data(title=title, file=file, dataset=new_dataset)
			new_data.save()
			messages.success(request, "Dataset created succesfully")
			return redirect('edit-dataset', id=id)
		else:
			messages.error(request, dataform.errors)
	context = {
		"dataform": dataform,
	}
	return render(request, "data-creation.html", context)

def partners_list(request):
	partners = Partner.objects.all()
	context = {
		"partners": partners,
	}
	return render(request, "list-partners.html", context)

def handler404(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response