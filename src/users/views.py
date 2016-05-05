from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ProfileForm, AffiliationForm, SelectRoleForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm, EventCreationForm, EditEventForm, RoleCreationForm, NewsCreationForm, FileCreationForm, NewsEditForm, SelectDatasetForm, MemberCreationForm, MemberSelectForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Profile_Event, Affiliation, Event, Dataset, Data, Partner, Event, Special_Issue, Workshop, Challenge, Role, News, File
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
from registration.backends.default.views import RegistrationView
from registration.models import RegistrationProfile
from registration.users import UserModel
from django.contrib.sites.models import Site
from registration import signals

class Backend(RegistrationView):
	def register(self, form):
		email = form.cleaned_data["email"]
		# password = User.objects.make_random_password()
		password = 'chalearn'
		username = email.split("@")[0]
		site = Site.objects.get_current()
		new_user_instance = (UserModel().objects.create_user(username=username,email=email,password=password))
		new_user = RegistrationProfile.objects.create_inactive_user(
			new_user=new_user_instance,
			site=site,
			send_email=self.SEND_ACTIVATION_EMAIL,
			request=self.request,
		)
		signals.user_registered.send(sender=self.__class__,user=new_user,request=self.request)
		return new_user

def home(request):
	news = News.objects.order_by('-upload_date')[:5]
	return render(request, "home.html", {"news": news}, context_instance=RequestContext(request));

def handler404(request):
	response = render_to_response('404.html', {}, context_instance=RequestContext(request))
	response.status_code = 404
	return response

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def user_list(request):
	users = User.objects.all().filter(is_staff=False)
	admins = User.objects.all().filter(is_staff=True)
	context = {
		"users": users,
		"admins": admins,
	}
	return render(request, "user/list.html", context, context_instance=RequestContext(request));

@login_required(login_url='/users/login/')
def user_edit(request, id=None):
	profile = Profile.objects.filter(user__id=id)[0]
	user = profile.user
	affiliation = profile.affiliation
	if affiliation==None:
		form = EditProfileForm(user=user)
	form = EditProfileForm(profile=profile, user=user, affiliation=affiliation)
	if request.method == 'POST':
		form = EditProfileForm(request.POST, profile=profile, user=user, affiliation=affiliation)
		if form.is_valid():
			username = form.cleaned_data["username"]
			email = form.cleaned_data["email"]
			if affiliation==None:
				affiliation = Affiliation()
			if 'first_name' in form.cleaned_data:
				profile.first_name = form.cleaned_data["first_name"]
			if 'last_name' in form.cleaned_data:
				profile.last_name = form.cleaned_data["last_name"]
			if 'staff' in form.cleaned_data:
				user.is_staff = form.cleaned_data["staff"]
			if 'avatar' in form.cleaned_data:
				profile.avatar = form.cleaned_data["avatar"]
			if 'bio' in form.cleaned_data:
				profile.bio = form.cleaned_data["bio"]
			if 'name' in form.cleaned_data:
				affiliation.name = form.cleaned_data["name"]
			if 'country' in form.cleaned_data:
				affiliation.country = form.cleaned_data["country"]
			if 'city' in form.cleaned_data:
				affiliation.city = form.cleaned_data["city"]
			user.username = username
			user.email = email
			user.save()
			affiliation.save()
			profile.user = user
			profile.affiliation = affiliation
			profile.save()
			return HttpResponseRedirect(reverse('home'))
	context = {
		"form": form,
		"user_edit": user.id
	}
	return render(request, "user/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def profile_edit(request, id=None):
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
			return HttpResponseRedirect(reverse('home'))
	context = {
		"form": form,
	}
	return render(request, "profile/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
@csrf_protect
def profile_select(request, id=None):
	choices = []
	event = Event.objects.filter(id=id)[0]
	roles = Role.objects.all()
	for r in roles:
	    choices.append((r.id, r.name))
	profile_events = Profile_Event.objects.filter(event_id=id)
	ids = []
	for p in profile_events:
		ids.append(p.profile.id)
	qset = Profile.objects.exclude(id__in = ids)
	selectRoleForm = SelectRoleForm(choices)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectRoleForm = SelectRoleForm(choices, request.POST)
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectRoleForm.is_valid() and selectform.is_valid():
			members = selectform.cleaned_data['email']
			role = Role.objects.filter(id=selectRoleForm.cleaned_data["role_select"])[0]
			for m in members:
				new_profile = Profile.objects.filter(id=m.id)[0]
				new_profile_event = Profile_Event.objects.create(profile=new_profile, event=event)
				role.profile_event = new_profile_event
				role.save()
			return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
	context = {
		"selectRoleForm": selectRoleForm,
		"selectform": selectform,
	}
	return render(request, "profile/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_list(request):
	datasets = Dataset.objects.all()
	context = {
		"datasets": datasets,
	}
	return render(request, "dataset/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_creation(request):
	datasetform = DatasetCreationForm()
	dataform = DataCreationForm()
	fileform = FileCreationForm()
	if request.method == 'POST':
		datasetform = DatasetCreationForm(request.POST)
		dataform = DataCreationForm(request.POST)
		fileform = FileCreationForm(request.POST, request.FILES)
		if datasetform.is_valid() and dataform.is_valid() and fileform.is_valid():
			dataset_title = datasetform.cleaned_data['dataset_title']
			desc = datasetform.cleaned_data['description']
			data_title = dataform.cleaned_data['data_title']
			file = fileform.cleaned_data['file']
			new_dataset = Dataset.objects.create(title=dataset_title, description=desc)
			new_data = Data.objects.create(title=data_title, dataset=new_dataset)
			File.objects.create(data=new_data, file=file)
			datasets = Dataset.objects.all()
			return HttpResponseRedirect(reverse('dataset_list'))
	context = {
		"datasetform": datasetform,
		"dataform": dataform,
		"fileform": fileform,
	}
	return render(request, "dataset/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_edit(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	context = {
		"dataset": dataset,
		"datas": datas,
	}
	return render(request, "dataset/edit.html", context, context_instance=RequestContext(request))

def dataset_detail(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	context = {
		"dataset": dataset,
		"datas": datas,
	}
	return render(request, "dataset/detail.html", context, context_instance=RequestContext(request))

def dataset_select(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	datasets = Dataset.objects.filter(~Q(track=challenge))
	choices = []
	for d in datasets:
		choices.append((d.id, d.title))
	form = SelectDatasetForm(choices)
	if request.method == 'POST':
		form = SelectDatasetForm(choices, request.POST)
		if form.is_valid():
			datasets_id = form.cleaned_data['select_dataset']
			for dataset_id in datasets_id:
				dataset = Dataset.objects.filter(id=dataset_id)[0]
				dataset.track.add(challenge)
				return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
	context = {
		"form": form,
	}
	return render(request, "dataset/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_creation(request, id=None):
	dataform = DataCreationForm()
	fileform = FileCreationForm()
	if request.method == 'POST':
		dataform = DataCreationForm(request.POST)
		fileform = FileCreationForm(request.POST, request.FILES)
		if dataform.is_valid() and fileform.is_valid():
			new_dataset = Dataset.objects.filter(id=id)[0]
			title = dataform.cleaned_data['data_title']
			file = fileform.cleaned_data['file']
			new_data = Data.objects.create(title=title, dataset=new_dataset)
			File.objects.create(file=file, data=new_data)
			return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':id}))
	context = {
		"dataform": dataform,
		"fileform": fileform,
		"dataset_id": id,
	}
	return render(request, "data/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_detail(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	files = File.objects.filter(data=data)
	fileform = FileCreationForm()
	if request.method == 'POST':
		fileform = FileCreationForm(request.POST, request.FILES)
		if fileform.is_valid():
			new_data = Data.objects.filter(id=id)[0]
			file = fileform.cleaned_data['file']
			File.objects.create(data=new_data, file=file)
	context = {
		"data": data,
		"files": files,
		"fileform": fileform,
		"dataset_id": dataset_id,
	}
	return render(request, "data/detail.html", context, context_instance=RequestContext(request))

def partner_list(request):
	partners = Partner.objects.all()
	context = {
		"partners": partners,
	}
	return render(request, "partner/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_list(request):
	events = Event.objects.all()
	context = {
		"events": events
	}
	return render(request, "event/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_creation(request):
	eventform = EventCreationForm()
	if request.method == 'POST':
		eventform = EventCreationForm(request.POST)
		if eventform.is_valid():
			title = eventform.cleaned_data['title']
			desc = eventform.cleaned_data['description']
			event_type = eventform.cleaned_data['event_type']
			if event_type == '1':
				Challenge.objects.create(title=title, description=desc)
			elif event_type == '2':
				Special_Issue.objects.create(title=title, description=desc)
			elif event_type == '3':
				Workshop.objects.create(title=title, description=desc)
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"eventform": eventform,
	}
	return render(request, "event/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_edit(request, id=None):
	event = Event.objects.filter(id=id)[0]
	challenge = Challenge.objects.filter(id=id)[0]
	members = Profile_Event.objects.filter(event_id=id)
	eventform = EditEventForm(event=event)
	news = News.objects.filter(event_id=id)
	datasets = Dataset.objects.filter(track=challenge)
	if request.method == 'POST':
		eventform = EditEventForm(request.POST, event=event)
		if eventform.is_valid():
			title = eventform.cleaned_data["title"]
			desc = eventform.cleaned_data["description"]
			event.title = title
			event.description = desc
			event.save()
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"eventform": eventform,
		"event": event,
		"members": members,
		"news": news,
		"datasets": datasets,
	}
	return render(request, "event/edit.html", context, context_instance=RequestContext(request))

def event_detail(request, id=None):
	event = Event.objects.filter(id=id)[0]
	challenge = Challenge.objects.filter(id=id)[0]
	members = Profile_Event.objects.filter(event_id=id)
	news = News.objects.filter(event_id=id)
	datasets = Dataset.objects.filter(track=challenge)
	context = {
		"event": event,
		"members": members,
		"news": news,
		"datasets": datasets,
	}
	return render(request, "event/detail.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def role_creation(request):
	roleform = RoleCreationForm()
	if request.method == 'POST':
		roleform = RoleCreationForm(request.POST)
		if roleform.is_valid():
			name = roleform.cleaned_data['name']
			role = Role(name=name)
			role.save()
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"roleform": roleform,
	}
	return render(request, "role/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def news_creation(request, id=None):
	event = Event.objects.filter(id=id)[0]
	newsform = NewsCreationForm()
	if request.method == 'POST':
		newsform = NewsCreationForm(request.POST)
		if newsform.is_valid():
			title = newsform.cleaned_data['title']
			desc = newsform.cleaned_data['description']
			news = News(title=title,description=desc,event=event)
			news.save()
			return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
	context = {
		"newsform": newsform,
	}
	return render(request, "news/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def news_edit(request, id=None):
	news = News.objects.filter(id=id)[0]
	newsform = NewsEditForm(news=news)
	if request.method == 'POST':
		newsform = NewsEditForm(request.POST, news=news)
		if newsform.is_valid():
			title = newsform.cleaned_data['title']
			desc = newsform.cleaned_data['description']
			news.title = title
			news.description = desc
			news.save()
			return HttpResponseRedirect(reverse('home'))
	context = {
		"newsform": newsform,
	}
	return render(request, "news/edit.html", context, context_instance=RequestContext(request))