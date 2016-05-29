from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse
from .forms import ProfileForm, AffiliationForm, SelectRoleForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm, EventCreationForm, EditEventForm, RoleCreationForm, NewsCreationForm, FileCreationForm, NewsEditForm, SelectDatasetForm, MemberCreationForm, MemberSelectForm, PartnerCreationForm, PartnerSelectForm, ScheduleCreationForm, ScheduleEditForm, DatasetEditForm, DataEditForm, TrackCreationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Profile_Event, Affiliation, Event, Dataset, Data, Partner, Event, Special_Issue, Workshop, Challenge, Role, News, File, Contact, Event_Partner, Schedule_Event, Track, Gallery_Image
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
			data_desc = dataform.cleaned_data['data_desc']
			new_dataset = Dataset.objects.create(title=dataset_title, description=desc)
			new_data = Data.objects.create(title=data_title, description=data_desc, dataset=new_dataset)
			file_name = fileform.cleaned_data['name']
			if fileform.cleaned_data['file']:
				file = fileform.cleaned_data['file']
				File.objects.create(name=file_name, file=file, data=new_data)				
			else:
				url = fileform.cleaned_data['url']
				File.objects.create(name=file_name, url=url, data=new_data)
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
	datasetform = DatasetEditForm(dataset=dataset)
	if request.method == 'POST':
		datasetform = DatasetEditForm(request.POST, dataset=dataset)
		if datasetform.is_valid():
			dataset_title = datasetform.cleaned_data['dataset_title']
			desc = datasetform.cleaned_data['description']
			dataset.title = dataset_title
			dataset.description = desc
			dataset.save()
			return HttpResponseRedirect(reverse('dataset_list'))
	context = {
		"datasetform": datasetform,
		"dataset": dataset,
		"datas": datas,
	}
	return render(request, "dataset/edit.html", context, context_instance=RequestContext(request))

def dataset_info(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	context = {
		"dataset": dataset,
		"datas": datas,
	}
	return render(request, "dataset/info.html", context, context_instance=RequestContext(request))

def dataset_source(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	context = {
		"dataset": dataset,
		"datas": datas,
	}
	return render(request, "dataset/source.html", context, context_instance=RequestContext(request))

def dataset_select(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	datasets = Dataset.objects.filter(~Q(track=challenge))
	choices = []
	for d in datasets:
		choices.append((d.id, d.title))
	form = SelectDatasetForm(choices)
	select = True
	if len(choices) < 1:
		select = False
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
		"select": select,
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
			desc = dataform.cleaned_data['data_desc']
			new_data = Data.objects.create(title=title, description=desc, dataset=new_dataset)
			file_name = fileform.cleaned_data['name']
			if fileform.cleaned_data['file']:
				file = fileform.cleaned_data['file']
				File.objects.create(name=file_name, file=file, data=new_data)				
			else:
				url = fileform.cleaned_data['url']
				File.objects.create(name=file_name, url=url, data=new_data)
			return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':id}))
	context = {
		"dataform": dataform,
		"fileform": fileform,
		"dataset_id": id,
	}
	return render(request, "data/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_edit(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	files = File.objects.filter(data=data)
	dataform = DataEditForm(data=data)
	if request.method == 'POST':
		dataform = DataEditForm(request.POST, data=data)
		if dataform.is_valid():
			data_title = dataform.cleaned_data['data_title']
			data_desc = dataform.cleaned_data['data_desc']
			data.title = data_title
			data.description = data_desc
			data.save()
	context = {
		"dataform": dataform,
		"data": data,
		"files": files,
		"dataset_id": dataset_id,
	}
	return render(request, "data/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def file_creation(request, id=None):
	data = Data.objects.filter(id=id)[0]
	fileform = FileCreationForm()
	if request.method == 'POST':
		fileform = FileCreationForm(request.POST, request.FILES)
		if fileform.is_valid():
			name = fileform.cleaned_data['name']
			if fileform.cleaned_data['file']:
				file = fileform.cleaned_data['file']
				File.objects.create(name=name, file=file, data=data)				
			else:
				url = fileform.cleaned_data['url']
				File.objects.create(name=name, url=url, data=data)
	context = {
		"fileform": fileform,
	}
	return render(request, "file/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_info(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	data = Data.objects.filter(id=id)[0]
	files = File.objects.filter(data=data)
	context = {
		"data": data,
		"dataset": dataset,
		"datas": datas,
		"files": files,
	}
	return render(request, "data/info.html", context, context_instance=RequestContext(request))

def partner_list(request):
	partners = Partner.objects.all()
	context = {
		"partners": partners,
	}
	return render(request, "partner/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def partner_creation(request):
	partnerform = PartnerCreationForm()
	if request.method == 'POST':
		partnerform = PartnerCreationForm(request.POST, request.FILES)
		if partnerform.is_valid():
			name = partnerform.cleaned_data['name']
			url = partnerform.cleaned_data['url']
			banner = partnerform.cleaned_data['banner']
			first_name = partnerform.cleaned_data['first_name']
			last_name = partnerform.cleaned_data['last_name']
			email = partnerform.cleaned_data['email']
			bio = partnerform.cleaned_data['bio']
			new_contact = Contact.objects.create(first_name=first_name, last_name=last_name, email=email, bio=bio)
			Partner.objects.create(name=name, url=url, banner=banner, contact=new_contact)
	context = {
		"partnerform": partnerform,
	}
	return render(request, "partner/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def partner_select(request, id=None):
	choices = []
	event = Event.objects.filter(id=id)[0]
	roles = Role.objects.all()
	for r in roles:
	    choices.append((r.id, r.name))
	event_partners = Event_Partner.objects.filter(event_id=id)
	ids = []
	for p in event_partners:
		ids.append(p.partner.id)
	qset = Partner.objects.exclude(id__in = ids)
	selectform = PartnerSelectForm(qset=qset)
	if request.method == 'POST':
		selectform = PartnerSelectForm(request.POST, qset=qset)
		if selectform.is_valid():
			partners = selectform.cleaned_data['partner']
			role = selectform.cleaned_data['role']
			for p in partners:
				new_partner = Partner.objects.filter(id=p.id)[0]
				new_event_partner = Event_Partner.objects.create(partner=new_partner, event=event, role=role)
	context = {
		"selectform": selectform,
	}
	return render(request, "partner/select.html", context, context_instance=RequestContext(request))

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
def event_proposal(request):
	eventform = EventCreationForm()
	if request.method == 'POST':
		eventform = EditEventForm(request.POST)
		if eventform.is_valid():
			title = eventform.cleaned_data['title']
			desc = eventform.cleaned_data['description']
			event_type = eventform.cleaned_data['event_type']
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"eventform": eventform,
	}
	return render(request, "event/proposal.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def challenge_edit(request, id=None):
	event = Event.objects.filter(id=id)[0]
	challenge = Challenge.objects.filter(id=id)[0]
	members = Profile_Event.objects.filter(event_id=id)
	eventform = EditEventForm(event=event)
	news = News.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge=challenge)
	partners = Event_Partner.objects.filter(event_id=id)
	program = Schedule_Event.objects.filter(event=challenge).order_by('-date')
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
		"tracks": tracks,
		"partners": partners,
		"program": program,
	}
	return render(request, "challenge/edit.html", context, context_instance=RequestContext(request))

def challenge_info(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
	}
	return render(request, "challenge/info.html", context, context_instance=RequestContext(request))

def track_info(request, id=None):
	track = Track.objects.filter(id=id)[0]
	context = {
		"track": track,
	}
	return render(request, "track/info.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def track_creation(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	datasets = Dataset.objects.all()
	choices = []
	for d in datasets:
	    choices.append((d.id, d.title))
	trackform = TrackCreationForm(choices)
	if request.method == 'POST':
		trackform = TrackCreationForm(choices, request.POST)
		if trackform.is_valid():
			title = trackform.cleaned_data['title']
			desc = trackform.cleaned_data['description']
			dataset_id = trackform.cleaned_data['dataset_select']
			dataset = Dataset.objects.filter(id=dataset_id)[0]
			Track.objects.create(title=title, description=desc, dataset=dataset, challenge=challenge)
	context = {
		"trackform": trackform,
	}
	return render(request, "track/creation.html", context, context_instance=RequestContext(request))

def challenge_members(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	profile_events = Profile_Event.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge__id=id)
	ids = []
	for p in profile_events:
		ids.append(p.id)
	members = Role.objects.filter(profile_event__in = ids)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"challenge": challenge,
		"members": members,
		"news": news,
		"tracks": tracks,		
	}
	return render(request, "challenge/members.html", context, context_instance=RequestContext(request))

def challenge_sponsors(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	sponsors = Event_Partner.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"challenge": challenge,
		"sponsors": sponsors,
		"news": news,
		"tracks": tracks,
	}
	return render(request, "challenge/sponsors.html", context, context_instance=RequestContext(request))

def challenge_program(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	program = Schedule_Event.objects.filter(event=challenge).order_by('-date')
	context = {
		"challenge": challenge,
		"news": news,
		"program": program,
		"tracks": tracks,				
	}
	return render(request, "challenge/program.html", context, context_instance=RequestContext(request))

def challenge_result(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,		
	}
	return render(request, "challenge/result.html", context, context_instance=RequestContext(request))

def workshop_edit(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	eventform = EditEventForm(event=workshop)
	program = Schedule_Event.objects.filter(event=workshop).order_by('-date')
	if request.method == 'POST':
		eventform = EditEventForm(request.POST, event=workshop)
		if eventform.is_valid():
			title = eventform.cleaned_data["title"]
			desc = eventform.cleaned_data["description"]
			workshop.title = title
			workshop.description = desc
			workshop.save()
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"eventform": eventform,
		"workshop": workshop,
		"program": program,
	}
	return render(request, "workshop/edit.html", context, context_instance=RequestContext(request))

def workshop_info(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"news": news,
	}
	return render(request, "workshop/info.html", context, context_instance=RequestContext(request))

def workshop_program(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	program = Schedule_Event.objects.filter(event=workshop).order_by('-date')
	context = {
		"workshop": workshop,
		"news": news,
		"program": program,
	}
	return render(request, "workshop/program.html", context, context_instance=RequestContext(request))

def workshop_speakers(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"news": news,
	}
	return render(request, "workshop/speakers.html", context, context_instance=RequestContext(request))

def workshop_gallery(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	images = Gallery_Image.objects.filter(workshop=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"news": news,
		"images": images,
	}
	return render(request, "workshop/gallery.html", context, context_instance=RequestContext(request))

def add_gallery_picture(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	images = Gallery_Image.objects.filter(workshop=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"news": news,
		"images": images,
	}
	return render(request, "workshop/add_picture.html", context, context_instance=RequestContext(request))

def special_issue_edit(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	members = Profile_Event.objects.filter(event_id=id)
	eventform = EditEventForm(event=issue)
	if request.method == 'POST':
		eventform = EditEventForm(request.POST, event=issue)
		if eventform.is_valid():
			title = eventform.cleaned_data["title"]
			desc = eventform.cleaned_data["description"]
			issue.title = title
			issue.description = desc
			issue.save()
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"eventform": eventform,
		"issue": issue,
		"members": members,
	}
	return render(request, "special_issue/edit.html", context, context_instance=RequestContext(request))

def special_issue_info(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"issue": issue,
		"news": news,
	}
	return render(request, "special_issue/info.html", context, context_instance=RequestContext(request))

def special_issue_members(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"issue": issue,
		"news": news,
	}
	return render(request, "special_issue/members.html", context, context_instance=RequestContext(request))

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

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_creation(request, id=None):
	event = Event.objects.filter(id=id)[0]
	scheduleform = ScheduleCreationForm()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			Schedule_Event.objects.create(title=title,description=desc,date=time,event=event)
			# return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
	context = {
		"scheduleform": scheduleform,
	}
	return render(request, "schedule/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='/users/login/')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_edit(request, id=None):
	# event = Event.objects.filter(id=id)[0]
	schedule = Schedule_Event.objects.filter(id=id)[0]
	scheduleform = ScheduleEditForm(schedule=schedule)
	if request.method == 'POST':
		scheduleform = ScheduleEditForm(request.POST, schedule=schedule)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			schedule.title = title
			schedule.description = desc
			schedule.date = time
			schedule.save()
			# return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
	context = {
		"scheduleform": scheduleform,
	}
	return render(request, "schedule/edit.html", context, context_instance=RequestContext(request))