from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse
from .forms import ProfileForm, AffiliationForm, SelectRoleForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm, EventCreationForm, EditEventForm, RoleCreationForm, NewsCreationForm, FileCreationForm, NewsEditForm, SelectDatasetForm, MemberCreationForm, MemberSelectForm, PartnerCreationForm, PartnerSelectForm, ScheduleCreationForm, ScheduleEditForm, DatasetEditForm, DataEditForm, TrackCreationForm, GalleryImageForm, TrackEditForm, RelationCreationForm, RelationEditForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Result, Score, Proposal, Profile_Event, Affiliation, Event, Dataset, Data, Partner, Event, Special_Issue, Workshop, Challenge, Role, News, File, Contact, Event_Partner, Schedule_Event, Track, Gallery_Image, Event_Relation
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
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse
from django.conf import settings
import csv
from decimal import Decimal

@require_POST
def file_upload(request):
	file_id = request.POST.get('file_id', '')
	file = upload_receive(request)
	new_file = File.objects.filter(id=file_id)[0]
	new_file.file = file
	new_file.save()
	basename = new_file.filename()
	file_dict = {
		'name' : basename,
		'size' : file.size,
		'url': settings.MEDIA_URL + basename,
		'thumbnailUrl': settings.MEDIA_URL + basename,
	}
	return UploadResponse(request, file_dict)

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

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def user_list(request):
	users = User.objects.all().filter(is_staff=False)
	admins = User.objects.all().filter(is_staff=True)
	context = {
		"users": users,
		"admins": admins,
	}
	return render(request, "user/list.html", context, context_instance=RequestContext(request));

@login_required(login_url='auth_login')
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
				if form.cleaned_data["staff"] == True:
					user.is_staff = True
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

@login_required(login_url='auth_login')
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

@login_required(login_url='auth_login')
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
				new_profile_event = Profile_Event.objects.create(profile=new_profile, event=event, role=role)
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"selectRoleForm": selectRoleForm,
		"selectform": selectform,
	}
	return render(request, "profile/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_list(request):
	datasets = Dataset.objects.all()
	context = {
		"datasets": datasets,
	}
	return render(request, "dataset/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_creation(request):
	datasetform = DatasetCreationForm()
	if request.method == 'POST':
		datasetform = DatasetCreationForm(request.POST)
		if datasetform.is_valid():
			dataset_title = datasetform.cleaned_data['dataset_title']
			desc = datasetform.cleaned_data['description']
			new_dataset = Dataset.objects.create(title=dataset_title, description=desc)
			return HttpResponseRedirect(reverse('data_creation', kwargs={'id':new_dataset.id}))
	context = {
		"datasetform": datasetform,
	}
	return render(request, "dataset/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_edit(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	datasetform = DatasetEditForm(dataset=dataset)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	relations = Event_Relation.objects.filter(dataset_associated=id)
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
		"schedule": schedule,
		"relations": relations,
	}
	return render(request, "dataset/edit.html", context, context_instance=RequestContext(request))

def dataset_desc(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	news = News.objects.filter(event_id=id)
	context = {
		"dataset": dataset,
		"news": news, 		
		"datas": datas,
	}
	return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))

def dataset_schedule(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	news = News.objects.filter(event_id=id)
	context = {
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule
	}
	return render(request, "dataset/schedule.html", context, context_instance=RequestContext(request))

def dataset_associated_events(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	relations = Event_Relation.objects.filter(dataset_associated__id=dataset_id)
	associated = Event_Relation.objects.filter(dataset_relation=dataset)
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule,
		"relations": relations,
		"associated": associated,
	}
	return render(request, "dataset/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_remove(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	dataset.delete()
	return HttpResponse(reverse('dataset_list'))

# def dataset_select(request, id=None):
# 	challenge = Challenge.objects.filter(id=id)[0]
# 	datasets = Dataset.objects.filter(~Q(track=challenge))
# 	choices = []
# 	for d in datasets:
# 		choices.append((d.id, d.title))
# 	form = SelectDatasetForm(choices)
# 	select = True
# 	if len(choices) < 1:
# 		select = False
# 	if request.method == 'POST':
# 		form = SelectDatasetForm(choices, request.POST)
# 		if form.is_valid():
# 			datasets_id = form.cleaned_data['select_dataset']
# 			for dataset_id in datasets_id:
# 				dataset = Dataset.objects.filter(id=dataset_id)[0]
# 				dataset.track.add(challenge)
# 				return HttpResponseRedirect(reverse('event_edit', kwargs={'id':id}))
# 	context = {
# 		"form": form,
# 		"select": select,
# 	}
# 	return render(request, "dataset/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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
			metric = dataform.cleaned_data['data_metric']
			software = dataform.cleaned_data['data_software']
			desc = dataform.cleaned_data['data_desc']
			new_data = Data.objects.create(title=title, description=desc, dataset=new_dataset, metric=metric, software=software)
			# file_name = fileform.cleaned_data['name']
			# if fileform.cleaned_data['file']:
			# 	file = fileform.cleaned_data['file']
			# 	File.objects.create(name=file_name, file=file, data=new_data)				
			# else:
			# 	url = fileform.cleaned_data['url']
			# 	File.objects.create(name=file_name, url=url, data=new_data)
			return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':id}))
	context = {
		"dataform": dataform,
		"fileform": fileform,
		"dataset_id": id,
	}
	return render(request, "data/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def data_remove(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	data.delete()
	return HttpResponse(reverse('dataset_edit', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
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
			software = dataform.cleaned_data['data_software']
			metric = dataform.cleaned_data['data_metric']
			data.title = data_title
			data.description = data_desc
			data.software = software
			data.metric = metric
			data.save()
			return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':id}))
	context = {
		"dataform": dataform,
		"data": data,
		"files": files,
		"dataset_id": dataset_id,
	}
	return render(request, "data/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def file_creation(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	fileform = FileCreationForm()
	create = True
	if request.method == 'POST':
		fileform = FileCreationForm(request.POST, request.FILES)
		if fileform.is_valid():
			create = False
			f_id = fileform.cleaned_data['f_id']
			if File.objects.filter(id=f_id).count > 0:
				new_file = File.objects.filter(id=f_id)[0]
			else:
				new_file = File.objects.create(data=data)
				f_id = new_file.id
			new_file.name = fileform.cleaned_data['name']
			if fileform.cleaned_data['url']:
				new_file.url = fileform.cleaned_data['url']
			new_file.save()
			return HttpResponseRedirect(reverse('data_edit', kwargs={'id':data.id, 'dataset_id': dataset_id}))
	if create:
		new_file = File.objects.create(data=data)
		f_id = new_file.id
	else:
		new_file = File.objects.filter(id=f_id)[0]
	context = {
		"data": data,
		"fileform": fileform,
		"new_file": new_file,
		"f_id": f_id,
	}
	return render(request, "file/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def file_remove(request, id=None, file_id=None, dataset_id=None):
	new_file = File.objects.filter(id=file_id)[0]
	new_file.delete()
	return HttpResponse(reverse('data_edit', kwargs={'id':id, 'dataset_id': dataset_id}))

def data_desc(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/desc.html", context, context_instance=RequestContext(request))

def data_software(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/software.html", context, context_instance=RequestContext(request))

def data_metric(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/metrics.html", context, context_instance=RequestContext(request))

def data_files(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	files = File.objects.filter(data=data)
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
		"files": files,
	}
	return render(request, "data/files.html", context, context_instance=RequestContext(request))

def data_results(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=dataset_id)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/results.html", context, context_instance=RequestContext(request))

def partner_list(request):
	partners = Partner.objects.all()
	context = {
		"partners": partners,
	}
	return render(request, "partner/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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
			return HttpResponseRedirect(reverse('partners_list'))
	context = {
		"partnerform": partnerform,
	}
	return render(request, "partner/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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
	selectRoleForm = SelectRoleForm(choices)
	selectform = PartnerSelectForm(qset=qset)
	if request.method == 'POST':
		selectRoleForm = SelectRoleForm(choices, request.POST)
		selectform = PartnerSelectForm(request.POST, qset=qset)
		if selectform.is_valid() and selectRoleForm.is_valid():
			partners = selectform.cleaned_data['partner']
			role = Role.objects.filter(id=selectRoleForm.cleaned_data["role_select"])[0]
			for p in partners:
				new_partner = Partner.objects.filter(id=p.id)[0]
				new_event_partner = Event_Partner.objects.create(partner=new_partner, event=event, role=role)
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"selectform": selectform,
		"selectRoleForm": selectRoleForm,
	}
	return render(request, "partner/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_list(request):
	events = Event.objects.all()
	context = {
		"events": events
	}
	return render(request, "event/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_remove(request, id=None):
	event = Event.objects.filter(id=id)[0]
	event.delete()
	if request.method == 'POST':
		return HttpResponse((reverse('event_list')))
		# return HttpResponse(reverse('event_list'))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_relation_remove(request, id=None, relation_id=None, dataset_id=None):
	relation = Event_Relation.objects.filter(id=relation_id)[0]
	relation.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit', kwargs={'id':id}))
	elif Dataset.objects.filter(id=dataset_id).count() > 0:
		return HttpResponse(reverse('dataset_edit', kwargs={'id':dataset_id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_member_remove(request, id=None, member_id=None):
	profile = Profile_Event.objects.filter(id=member_id)[0]
	profile.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_news_remove(request, id=None, news_id=None):
	news = News.objects.filter(id=news_id)[0]
	news.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))
@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_schedule_remove(request, dataset_id=None, schedule_id=None):
	program = Schedule_Event.objects.filter(id=schedule_id)[0]
	program.delete()
	return HttpResponse(reverse('dataset_edit', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_program_remove(request, id=None, program_id=None):
	program = Schedule_Event.objects.filter(id=program_id)[0]
	program.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_partner_remove(request, id=None, partner_id=None):
	partner = Event_Partner.objects.filter(id=partner_id)[0]
	partner.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
def event_proposal_creation(request):
	eventform = EventCreationForm()
	if request.method == 'POST':
		eventform = EventCreationForm(request.POST)
		if eventform.is_valid():
			title = eventform.cleaned_data['title']
			desc = eventform.cleaned_data['description']
			event_type = eventform.cleaned_data['event_type']
			Proposal.objects.create(title=title,description=desc,type=event_type)
			return HttpResponseRedirect(reverse('home'))
	context = {
		"eventform": eventform,
	}
	return render(request, "proposal/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def event_proposal_list(request):
	challenge_proposals = Proposal.objects.filter(type='1')
	workshop_proposals = Proposal.objects.filter(type='3')
	issue_proposals = Proposal.objects.filter(type='2')
	context = {
		"challenge_proposals": challenge_proposals,
		"workshop_proposals": workshop_proposals,
		"issue_proposals": issue_proposals,
	}
	return render(request, "proposal/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def event_proposal_detail(request, id=None):
	proposal = Proposal.objects.filter(id=id)[0]
	context = {
		"proposal": proposal,
	}
	return render(request, "proposal/detail.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def challenge_edit(request, id=None):
	event = Event.objects.filter(id=id)[0]
	challenge = Challenge.objects.filter(id=id)[0]
	members = Profile_Event.objects.filter(event_id=id)
	eventform = EditEventForm(event=event)
	news = News.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge=challenge)
	partners = Event_Partner.objects.filter(event_id=id)
	schedule = Schedule_Event.objects.filter(event_schedule=challenge,schedule_event_parent=None).order_by('date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	if request.method == 'POST':
		eventform = EditEventForm(request.POST, request.FILES, event=event)
		if eventform.is_valid():
			title = eventform.cleaned_data["title"]
			desc = eventform.cleaned_data["description"]
			if eventform.cleaned_data["file"]:
				Result.objects.filter(challenge=challenge).delete()
				csv_file = csv.reader(eventform.cleaned_data["file"])
				titles = True
				names = None
				for l in csv_file:
					if len(l) > 1:
						if titles:
							names = l
							titles = False
						else:
							username = l[0]
							result = Result.objects.create(user=l[0], challenge=challenge)
							i = 1
							for item in l:
								element = item.split()
								if len(element) > 0:
									element = element[0]
									try:
										digit = float(element)
										Score.objects.create(name=names[i], result=result, score=digit)
										i+=1
									except ValueError:
										continue
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
		"schedule": schedule,
		"relations": relations,
	}
	return render(request, "challenge/edit.html", context, context_instance=RequestContext(request))

def challenge_desc(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
	}
	return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))

def challenge_associated_events(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated=challenge)
	associated = Event_Relation.objects.filter(challenge_relation=challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"relations": relations,
		"associated": associated,
	}
	return render(request, "challenge/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_relation_creation(request, id=None, dataset_id=None):
	if id==None:
		events = Event.objects.all()
	else:
		events = Event.objects.exclude(id__in = [id])
	datasets = Dataset.objects.all()
	print datasets
	print '--------'
	choices = []
	for x in events:
		choices.append((x.id, x.title)) 
	for d in datasets:
		choices.append((d.id, d.title)) 
	relationform = RelationCreationForm(choices)
	if request.method == 'POST':
		relationform = RelationCreationForm(choices,request.POST)
		if relationform.is_valid():
			desc = relationform.cleaned_data['description']
			event_id = relationform.cleaned_data['event']
			if dataset_id == None:
				event_associated = Event.objects.filter(id=id)[0]	
				if Challenge.objects.filter(id=event_id).count() > 0:
					relation = Challenge.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(event_associated=event_associated,challenge_relation=relation,description=desc)
				elif Workshop.objects.filter(id=event_id).count() > 0:
					relation = Workshop.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(event_associated=event_associated,workshop_relation=relation,description=desc)
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					relation = Special_Issue.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(event_associated=event_associated,issue_relation=relation,description=desc)
				elif Dataset.objects.filter(id=event_id).count() > 0:
					relation = Dataset.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(event_associated=event_associated,dataset_relation=relation,description=desc)
			else:
				dataset_associated = Dataset.objects.filter(id=dataset_id)[0]
				if Challenge.objects.filter(id=event_id).count() > 0:
					relation = Challenge.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(dataset_associated=dataset_associated,challenge_relation=relation,description=desc)
				elif Workshop.objects.filter(id=event_id).count() > 0:
					relation = Workshop.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(dataset_associated=dataset_associated,workshop_relation=relation,description=desc)
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					relation = Special_Issue.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(dataset_associated=dataset_associated,issue_relation=relation,description=desc)
				elif Dataset.objects.filter(id=event_id).count() > 0:
					relation = Dataset.objects.filter(id=event_id)[0]
					Event_Relation.objects.create(dataset_associated=dataset_associated,dataset_relation=relation,description=desc)

			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':id}))
			elif Dataset.objects.filter(id=dataset_id).count() > 0:
				return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':dataset_id}))
			else:
				return HttpResponseRedirect(reverse('home'))

	context = {
		"relationform": relationform,
	}
	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_relation_edit(request, id=None, relation_id=None):
	relation = Event_Relation.objects.filter(id=relation_id)[0]
	events = Event.objects.exclude(id__in = [id])
	datasets = Dataset.objects.exclude(id__in = [id])
	choices = []
	for x in events:
		choices.append((x.id, x.title)) 
	for d in datasets:
		choices.append((d.id, d.title)) 
	relationform = RelationEditForm(choices, relation=relation)
	if request.method == 'POST':
		relationform = RelationEditForm(choices, request.POST, relation=relation)
		if relationform.is_valid():
			event_associated = Event.objects.filter(id=id)[0]
			desc = relationform.cleaned_data['description']
			event_id = relationform.cleaned_data['event']
			relation.description = desc  
			if Challenge.objects.filter(id=event_id).count() > 0:
				relation = Challenge.objects.filter(id=event_id)[0]
				relation.challenge_relation=relation
			elif Workshop.objects.filter(id=event_id).count() > 0:
				relation = Workshop.objects.filter(id=event_id)[0]
				relation.workshop_relation=relation
			elif Special_Issue.objects.filter(id=event_id).count() > 0:
				relation = Special_Issue.objects.filter(id=event_id)[0]
				relation.issue_relation=relation
			elif Dataset.objects.filter(id=event_id).count() > 0:
				relation = Dataset.objects.filter(id=event_id)[0]
				relation.dataset_relation=relation
			relation.save()
	context = {
		"relationform": relationform,
	}
	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

def track_desc(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	# tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
		# "tracks": tracks,
	}
	return render(request, "track/desc.html", context, context_instance=RequestContext(request))

def track_metrics(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	# tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
		# "tracks": tracks,
	}
	return render(request, "track/metrics.html", context, context_instance=RequestContext(request))

def track_baseline(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	# tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
		# "tracks": tracks,
	}
	return render(request, "track/baseline.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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
			metrics = trackform.cleaned_data['metrics']
			baseline = trackform.cleaned_data['baseline']
			dataset_id = trackform.cleaned_data['dataset_select']
			dataset = Dataset.objects.filter(id=dataset_id)[0]
			Track.objects.create(title=title, description=desc, metrics=metrics, baseline=baseline, dataset=dataset, challenge=challenge)
			return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
	context = {
		"trackform": trackform,
	}
	return render(request, "track/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def track_edit(request, id=None, track_id=None):
	# challenge = Challenge.objects.filter(id=id)[0]
	track = Track.objects.filter(id=track_id)[0]
	datasets = Dataset.objects.all()
	choices = []
	for d in datasets:
	    choices.append((d.id, d.title))
	trackform = TrackEditForm(choices, track=track)
	if request.method == 'POST':
		trackform = TrackEditForm(choices, request.POST, track=track)
		if trackform.is_valid():
			title = trackform.cleaned_data['title']
			desc = trackform.cleaned_data['description']
			metrics = trackform.cleaned_data['metrics']
			baseline = trackform.cleaned_data['baseline']
			dataset_id = trackform.cleaned_data['dataset_select']
			track.title = title
			track.description = desc 
			track.metrics = metrics
			track.baseline = baseline
			track.dataset = Dataset.objects.filter(id=dataset_id)[0]
			track.save()
			return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
	context = {
		"trackform": trackform,
	}
	return render(request, "track/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def track_remove(request, id=None, track_id=None):
	track = Track.objects.filter(id=track_id)[0]
	track.delete()
	return HttpResponse(reverse('challenge_edit', kwargs={'id':id}))

def challenge_members(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	members = Profile_Event.objects.filter(event = challenge)
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

def challenge_schedule(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	# program = []
	schedule = Schedule_Event.objects.filter(event_schedule=challenge,schedule_event_parent=None).order_by('date')
	# for e in events:
	# 	sub_events = Schedule_Event.objects.filter(schedule_event_parent=e)
	# 	program.append([e,sub_events])
	context = {
		"challenge": challenge,
		"news": news,
		"schedule": schedule,
		"tracks": tracks,				
	}
	return render(request, "challenge/schedule.html", context, context_instance=RequestContext(request))

def challenge_result(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	scores = Score.objects.filter(result__challenge=challenge)
	results = Result.objects.filter(challenge=challenge)
	result = Result.objects.filter(challenge=challenge)[0]
	qset = Score.objects.filter(result=result)
	names = []
	for n in qset:
		names.append(n.name)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"scores": scores,	
		"names": names,	
		"results": results,
	}
	return render(request, "challenge/result.html", context, context_instance=RequestContext(request))

def workshop_edit(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	speakers = Profile_Event.objects.filter(role__name='speaker')
	eventform = EditEventForm(event=workshop)
	program = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
	news = News.objects.filter(event_id=id)
	images = Gallery_Image.objects.filter(workshop=workshop)
	schedule = Schedule_Event.objects.filter(event_schedule=workshop,schedule_event_parent=None).order_by('date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
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
		"speakers": speakers,
		"workshop": workshop,
		"program": program,
		"news": news,
		"images": images, 
		"schedule": schedule,
		"relations": relations,
	}
	return render(request, "workshop/edit.html", context, context_instance=RequestContext(request))

def workshop_desc(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"news": news,
	}
	return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))

def workshop_schedule(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=workshop,schedule_event_parent=None).order_by('date')
	context = {
		"workshop": workshop,
		"news": news,
		"schedule": schedule,
	}
	return render(request, "workshop/schedule.html", context, context_instance=RequestContext(request))

def workshop_associated_events(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(workshop_relation=workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"relations": relations,
		"associated": associated,
	}
	return render(request, "workshop/relation.html", context, context_instance=RequestContext(request))

def workshop_program(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	# program = []
	# events = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
	# for e in events:
	# 	sub_events = Schedule_Event.objects.filter(schedule_event_parent=e)
	# 	program.append([e,sub_events])
	program = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
	context = {
		"workshop": workshop,
		"news": news,
		"program": program,
	}
	return render(request, "workshop/program.html", context, context_instance=RequestContext(request))

def workshop_speakers(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	speakers = Profile_Event.objects.filter(role__name='speaker')
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"workshop": workshop,
		"speakers": speakers,
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

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def add_gallery_picture(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	form = GalleryImageForm()
	if request.method == 'POST':
		form = GalleryImageForm(request.POST, request.FILES)
		if form.is_valid():
			image = form.cleaned_data["image"]
			desc = form.cleaned_data["desc"]
			Gallery_Image.objects.create(image=image, description=desc, workshop=workshop)
			return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
	context = {
		"workshop": workshop,
		"form": form,
	}
	return render(request, "workshop/add_picture.html", context, context_instance=RequestContext(request))

def speaker_select(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	profile_events = Profile_Event.objects.filter(event_id=id)
	ids = []
	for p in profile_events:
		if p.role.name == 'speaker':
			ids.append(p.profile.id)
	qset = Profile.objects.exclude(id__in = ids)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectform.is_valid():
			speakers = selectform.cleaned_data['email']
			for s in speakers:
				new_profile = Profile.objects.filter(id=s.id)[0]
				new_role, created = Role.objects.get_or_create(name='speaker')
				new_profile_event = Profile_Event.objects.create(profile=new_profile, event=workshop, role=new_role)
			return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
	context = {
		"workshop": workshop,
		"selectform": selectform,
	}
	return render(request, "speaker/select.html", context, context_instance=RequestContext(request))

def speaker_creation(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	context = {
		"workshop": workshop,
	}
	return render(request, "workshop/speakers.html", context, context_instance=RequestContext(request))

def special_issue_edit(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id)
	members = Profile_Event.objects.filter(event_id=id)
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	eventform = EditEventForm(event=issue)
	relations = Event_Relation.objects.filter(event_associated__id=id) 
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
		"news": news,
		"members": members,
		"schedule": schedule,
		"relations": relations,
	}
	return render(request, "special_issue/edit.html", context, context_instance=RequestContext(request))

def special_issue_desc(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	context = {
		"issue": issue,
		"news": news,
	}
	return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))

def special_issue_members(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	members = Profile_Event.objects.filter(event = issue)
	context = {
		"issue": issue,
		"news": news,
		"members": members,
	}
	return render(request, "special_issue/members.html", context, context_instance=RequestContext(request))

def special_issue_schedule(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	context = {
		"issue": issue,
		"news": news,
		"schedule": schedule,
	}
	return render(request, "special_issue/schedule.html", context, context_instance=RequestContext(request))

def special_issue_associated_events(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(issue_relation=issue)
	context = {
		"issue": issue,
		"news": news,
		"relations": relations,
		"associated": associated,
	}
	return render(request, "special_issue/relations.html", context, context_instance=RequestContext(request))
	
@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def role_creation(request):
	roleform = RoleCreationForm()
	if request.method == 'POST':
		roleform = RoleCreationForm(request.POST)
		if roleform.is_valid():
			name = roleform.cleaned_data['name']
			role = Role.objects.create(name=name)
			return HttpResponseRedirect(reverse('event_list'))
	context = {
		"roleform": roleform,
	}
	return render(request, "role/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"newsform": newsform,
	}
	return render(request, "news/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
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

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_creation(request, dataset_id=None, event_id=None):
	scheduleform = ScheduleCreationForm()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			if dataset_id==None:
				event = Event.objects.filter(id=event_id)[0]
				new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,event_schedule=event)
				if Challenge.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':event_id}))
				elif Workshop.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':event_id}))
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':event_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
			else:
				dataset = Dataset.objects.filter(id=dataset_id)[0]
				new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,dataset_schedule=dataset)
				if Dataset.objects.filter(id=dataset_id).count() > 0:
					return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':dataset_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
	context = {
		"scheduleform": scheduleform,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def program_creation(request, id=None):
	event = Event.objects.filter(id=id)[0]
	scheduleform = ScheduleCreationForm()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,event_program=event)
			return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':id}))
			# if 'save' in request.POST:
			# 	return HttpResponseRedirect(reverse('home'))
			# elif 'save_continue' in request.POST:
			# 	return HttpResponseRedirect(reverse('subevent_creation', kwargs={'event_id':id,'program_id':new_event.id}))
	context = {
		"scheduleform": scheduleform,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_edit(request, schedule_id=None, dataset_id=None, event_id=None):
	# event = Event.objects.filter(id=id)[0]
	schedule = Schedule_Event.objects.filter(id=schedule_id)[0]
	scheduleform = ScheduleEditForm(schedule=schedule)
	# subevents = Schedule_Event.objects.filter(schedule_event_parent=schedule).order_by('date')
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
			if dataset_id != None:
				if Dataset.objects.filter(id=dataset_id).count() > 0:
					return HttpResponseRedirect(reverse('dataset_edit', kwargs={'id':dataset_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
			else:
				if Challenge.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('challenge_edit', kwargs={'id':event_id}))
				elif Workshop.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('workshop_edit', kwargs={'id':event_id}))
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('special_issue_edit', kwargs={'id':event_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
	context = {
		"scheduleform": scheduleform,
		# "event": event,
		"schedule": schedule,
		# "subevents": subevents,
	}
	return render(request, "program/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def subevent_creation(request, event_id=None, program_id=None):
	event = Event.objects.filter(id=event_id)[0]
	parent_event = Schedule_Event.objects.filter(id=program_id)[0]
	scheduleform = ScheduleCreationForm()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			Schedule_Event.objects.create(title=title,description=desc,date=time,event_program=event,schedule_event_parent=parent_event)
			return HttpResponseRedirect(reverse('program_edit', kwargs={'id':event_id, 'program_id': program_id}))
	context = {
		"scheduleform": scheduleform,
	}
	return render(request, "program/creation-subevent.html", context, context_instance=RequestContext(request))