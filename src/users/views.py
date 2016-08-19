from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse
from .forms import PublicationEditForm, PublicationEventCreationForm, PublicationCreationForm, SubmissionEditForm, ColEditForm, EditChallengeResult, ProfileForm, AffiliationForm, SelectRoleForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm, EventCreationForm, EditEventForm, RoleCreationForm, NewsCreationForm, FileCreationForm, NewsEditForm, SelectDatasetForm, MemberCreationForm, MemberSelectForm, PartnerCreationForm, PartnerSelectForm, ScheduleCreationForm, ScheduleEditForm, DatasetEditForm, DataEditForm, TrackCreationForm, GalleryImageForm, TrackEditForm, RelationCreationForm, RelationEditForm, SubmissionCreationForm, SubmissionScoresForm, ResultEditForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Publication, Profile_Dataset, Submission, Col, Profile, Result, Score, Proposal, Profile_Event, Affiliation, Event, Dataset, Data, Partner, Event, Special_Issue, Workshop, Challenge, Role, News, File, Contact, Event_Partner, Schedule_Event, Track, Gallery_Image, Event_Relation
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
import xlwt
import xlsxwriter
import StringIO
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
		form = EditProfileForm(request.POST, request.FILES, profile=profile, user=user, affiliation=affiliation)
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

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_user_csv(request):
	users = Profile.objects.all()
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="users.csv"'
	writer = csv.writer(response)
	# response.write(u'\ufeff'.encode('utf8'))
	writer.writerow(['ID','Username','First name','Last name','Email','Affiliation','Events'])
	for u in users:
		events = ''
		profile_events = Profile_Event.objects.filter(profile=u).exclude(event=None)
		i=0
		for p in profile_events:
			if i==(len(profile_events)-1):
				events += (p.event.title.encode('utf8')+'('+p.role.name.encode('utf8')+')')
			else:
				events += (p.event.title.encode('utf8')+'('+p.role.name.encode('utf8')+'), ')
			i+=1
		if u.affiliation.city and u.affiliation.country:
			writer.writerow([u.pk,u.user.username.encode('utf8'),u.first_name.encode('utf8'),u.last_name.encode('utf8'),u.user.email,(u.affiliation.name.encode('utf8')+', '+u.affiliation.city.encode('utf8')+', '+u.affiliation.country.encode('utf8')),events])
		else:
			writer.writerow([u.pk,u.user.username.encode('utf8'),u.first_name.encode('utf8'),u.last_name.encode('utf8'),u.user.email,(u.affiliation.name.encode('utf8')),events])
	return response

def export_members_csv(request, event_id=None):
	event = Event.objects.filter(id=event_id)[0]
	profile_events = Profile_Event.objects.filter(event__id=event_id)
	response = HttpResponse(content_type='text/csv')
	filename = (event.title).replace(" ", "-")+'_members.csv'
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	writer = csv.writer(response)
	response.write(u'\ufeff'.encode('utf8'))
	writer.writerow(['ID','Username','First name','Last name','Email','Affiliation','Role'])
	for u in profile_events:
		role_name = u.role.name
		u = u.profile
		if u.affiliation.city and u.affiliation.country:
			writer.writerow([u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country),role_name])
		else:
			writer.writerow([u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name),role_name])
	return response

def export_participants_csv(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	submissions = Submission.objects.filter(dataset__id=dataset_id)
	response = HttpResponse(content_type='text/csv')
	filename = (dataset.title).replace(" ", "-")+'_participants.csv'
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	writer = csv.writer(response)
	response.write(u'\ufeff'.encode('utf8'))
	writer.writerow(['ID','Username','First name','Last name','Email','Affiliation'])
	for u in submissions:
		u = Profile.objects.filter(user=u.user)[0]
		if u.affiliation.city and u.affiliation.country:
			writer.writerow([u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country)])
		else:
			writer.writerow([u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name)])
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_user_xls(request):
	users = Profile.objects.all()
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="users.xls"'

	workbook = xlwt.Workbook()
	worksheet = workbook.add_sheet("Users")
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation','Events']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in users:
		row_num += 1
		events = ''
		profile_events = Profile_Event.objects.filter(profile=u).exclude(event=None)
		i=0
		for p in profile_events:
			if i==(len(profile_events)-1):
				events += (p.event.title+'('+p.role.name+')')
			else:
				events += (p.event.title+'('+p.role.name+'), ')
			i+=1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country),events]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name),events]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.save(response)
	return response

def export_members_xls(request, event_id=None):
	event = Event.objects.filter(id=event_id)[0]
	profile_events = Profile_Event.objects.filter(event__id=event_id)
	response = HttpResponse(content_type='application/vnd.ms-excel')
	filename = (event.title).replace(" ", "-")+'_members.xls'
	response['Content-Disposition'] = 'attachment; filename=%s' % filename

	workbook = xlwt.Workbook()
	worksheet = workbook.add_sheet("Event members")
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation','Role']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in profile_events:
		role_name = u.role.name
		u = u.profile
		row_num += 1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country),role_name]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name),role_name]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.save(response)
	return response

def export_participants_xls(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	submissions = Submission.objects.filter(dataset__id=dataset_id)
	response = HttpResponse(content_type='application/vnd.ms-excel')
	filename = (dataset.title).replace(" ", "-")+'_participants.xls'
	response['Content-Disposition'] = 'attachment; filename=%s' % filename

	workbook = xlwt.Workbook()
	worksheet = workbook.add_sheet("Dataset participants")
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in submissions:
		u = Profile.objects.filter(user=u.user)[0]
		row_num += 1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country)]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name)]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.save(response)
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_user_xlsx(request):
	users = Profile.objects.all()	
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('Users')
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation','Events']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in users:
		row_num += 1
		events = ''
		profile_events = Profile_Event.objects.filter(profile=u).exclude(event=None)
		i=0
		for p in profile_events:
			if i==(len(profile_events)-1):
				events += (p.event.title+'('+p.role.name+')')
			else:
				events += (p.event.title+'('+p.role.name+'), ')
			i+=1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country),events]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name),events]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.close()
	output.seek(0)
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
	return response

def export_members_xlsx(request, event_id=None):
	event = Event.objects.filter(id=event_id)[0]
	profile_events = Profile_Event.objects.filter(event__id=event_id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('Event members')
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation','Role']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in profile_events:
		role_name = u.role.name
		u = u.profile		
		row_num += 1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country),role_name]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name),role_name]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.close()
	output.seek(0)
	filename = (event.title).replace(" ", "-")+'_members.xlsx'
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

def export_participants_xlsx(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	submissions = Submission.objects.filter(dataset__id=dataset_id)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('Dataset participants')
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in submissions:
		u = Profile.objects.filter(user=u.user)[0]	
		row_num += 1
		if u.affiliation.city and u.affiliation.country:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name+', '+u.affiliation.city+', '+u.affiliation.country)]
		else:
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,(u.affiliation.name)]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.close()
	output.seek(0)
	filename = (dataset.title).replace(" ", "-")+'_participants.xlsx'
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename=%s' % filename

	return response

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
@csrf_protect
def profile_select(request, id=None):
	c = None
	w = None
	s = None
	if Challenge.objects.filter(id=id).count() > 0:
		c = Challenge.objects.filter(id=id)[0]
	elif Workshop.objects.filter(id=id).count() > 0:
		w = Workshop.objects.filter(id=id)[0]
	elif Special_Issue.objects.filter(id=id).count() > 0:
		s = Special_Issue.objects.filter(id=id)[0]
	choices = []
	event = Event.objects.filter(id=id)[0]
	roles = Role.objects.all()
	for r in roles:
	    choices.append((r.id, r.name))
	profile_events = Profile_Event.objects.filter(event_id=id)
	ids = []
	for p in profile_events:
		ids.append(p.profile.id)
	# qset = Profile.objects.exclude(id__in = ids)
	qset = User.objects.all()
	selectRoleForm = SelectRoleForm(choices)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectRoleForm = SelectRoleForm(choices, request.POST)
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectRoleForm.is_valid() and selectform.is_valid():
			members = selectform.cleaned_data['email']
			role = Role.objects.filter(id=selectRoleForm.cleaned_data["role_select"])[0]
			for m in members:
				user = User.objects.filter(id=m.id)[0]
				new_profile = Profile.objects.filter(user=user)[0]
				new_profile_event = Profile_Event.objects.create(profile=new_profile, event=event, role=role)
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit_members', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_members', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_members', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"selectRoleForm": selectRoleForm,
		"selectform": selectform,
		"c": c,
		"w": w,
		"s": s,
	}
	return render(request, "profile/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@csrf_protect
def dataset_profile_select(request, dataset_id=None):
	d = Dataset.objects.filter(id=dataset_id)[0]
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	profile_dataset = Profile_Dataset.objects.filter(dataset=dataset)
	ids = []
	for p in profile_dataset:
		if p.role.name == 'admin':
			ids.append(p.profile.id)
	qset = Profile.objects.exclude(id__in = ids)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectform.is_valid():
			admins = selectform.cleaned_data['email']
			for a in admins:
				new_profile = Profile.objects.filter(id=a.id)[0]
				new_role, created = Role.objects.get_or_create(name='admin')
				new_profile_event = Profile_Dataset.objects.create(profile=new_profile, dataset=dataset, role=new_role)
			return HttpResponseRedirect(reverse('dataset_edit_members', kwargs={'id':dataset_id}))
	context = {
		"dataset": dataset,
		"selectform": selectform,
		"d": d,
	}
	return render(request, "dataset/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_list(request):
	datasets = Dataset.objects.all()
	context = {
		"datasets": datasets,
	}
	return render(request, "dataset/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_creation(request):
	datasetform = DatasetCreationForm()
	if request.method == 'POST':
		datasetform = DatasetCreationForm(request.POST)
		if datasetform.is_valid():
			dataset_title = datasetform.cleaned_data['dataset_title']
			desc = datasetform.cleaned_data['description']
			cols = datasetform.cleaned_data['cols']
			new_dataset = Dataset.objects.create(title=dataset_title, description=desc)
			i = 1
			while i <= cols:
				Col.objects.create(dataset=new_dataset, name='col'+str(i))
				i+=1
			return HttpResponseRedirect(reverse('data_creation', kwargs={'id':new_dataset.id}))
	context = {
		"datasetform": datasetform,
	}
	return render(request, "dataset/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
		if len(profile_dataset) > 0:
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)[0]
			if not profile_dataset.is_admin():
				return HttpResponseRedirect(reverse('home'))
		else:
			return HttpResponseRedirect(reverse('home'))
	profile_dataset = None
	if request.user and (not request.user.is_anonymous()):
		profile = Profile.objects.filter(user=request.user)
		profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
		if len(profile_dataset) > 0:
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)[0]
			if not profile_dataset.is_admin():
				profile_dataset = None
		else:
			profile_dataset = None
	datas = Data.objects.all().filter(dataset=dataset)
	datasetform = DatasetEditForm(dataset=dataset)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	relations = Event_Relation.objects.filter(dataset_associated=id)
	news = News.objects.filter(dataset_id=id)
	members = Profile_Dataset.objects.filter(dataset=dataset)
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
		"news": news,
		"members": members,
		"profile_dataset": profile_dataset,
	}
	return render(request, "dataset/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_desc(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
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
		return render(request, "dataset/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_schedule(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
		context = {
			"dataset": dataset,
			"datas": datas,
			"schedule": schedule,
		}
		return render(request, "dataset/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_relations(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		relations = Event_Relation.objects.filter(dataset_associated=dataset)
		associated = Event_Relation.objects.filter(dataset_relation=dataset)
		context = {
			"dataset": dataset,
			"datas": datas,
			"relations": relations,
			"associated": associated
		}
		return render(request, "dataset/edit/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_datas(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		context = {
			"dataset": dataset,
			"datas": datas,
		}
		return render(request, "dataset/edit/datas.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_members(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		members = Profile_Dataset.objects.filter(dataset=dataset)
		context = {
			"dataset": dataset,
			"datas": datas,
			"members": members
		}
		return render(request, "dataset/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_results(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		submission = Submission.objects.filter(dataset=dataset)
		scores = None
		names = None
		submissions = None
		if submission:
			submission = Submission.objects.filter(dataset=dataset)[0]
			submissions = Submission.objects.filter(dataset=dataset)
			scores = []
			for s in submissions:
				sub_results = Score.objects.filter(submission=s)
				scores.append((s,sub_results))
		names = Col.objects.all().filter(dataset=dataset)
		context = {
			"dataset": dataset,
			"datas": datas,
			"names": names,	
			"scores": scores,
		}
		return render(request, "dataset/edit/results.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_news(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	news = News.objects.filter(dataset_id=id)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		context = {
			"news": news,
			"dataset": dataset,
			"datas": datas,
		}
		return render(request, "dataset/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_publications(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	news = News.objects.filter(dataset_id=id)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication.objects.filter(dataset=id)
		context = {
			"news": news,
			"dataset": dataset,
			"datas": datas,
			"publications": publications,
		}
		return render(request, "dataset/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_col(request, id=None, col_id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		col = Col.objects.filter(id=col_id)[0]
		colform = ColEditForm(col=col)
		if request.method == 'POST':
			colform = ColEditForm(request.POST, col=col)
			if colform.is_valid():
				name = colform.cleaned_data['name']
				col.name = name
				col.save()
				return HttpResponseRedirect(reverse('dataset_edit_results', kwargs={'id':id}))
		context = {
			"colform": colform,
			"dataset": dataset,
			"datas": datas,
		}
		return render(request, "dataset/edit/col.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_submission(request, id=None, submission_id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		submission = Submission.objects.filter(id=submission_id)[0]
		subform = SubmissionEditForm(submission=submission)
		if request.method == 'POST':
			subform = SubmissionEditForm(request.POST, submission=submission)
			if subform.is_valid():
				source_code = subform.cleaned_data['source_code']
				publication = subform.cleaned_data['publication']
				sub_file = subform.cleaned_data['sub_file']
				submission.source_code = source_code
				submission.publication = publication
				if sub_file:
					submission.sub_file = sub_file
				submission.save()
				return HttpResponseRedirect(reverse('dataset_edit_results', kwargs={'id':id}))
		context = {
			"subform": subform,
			"dataset": dataset,
			"datas": datas,
		}
		return render(request, "dataset/edit/submission.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_publish(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	dataset.is_public = True
	dataset.save()
	return HttpResponseRedirect(reverse('dataset_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def dataset_unpublish(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	dataset.is_public = False
	dataset.save()
	return HttpResponseRedirect(reverse('dataset_edit_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def data_publish(request, dataset_id=None, id=None):
	data = Data.objects.filter(id=id)[0]
	data.is_public = True
	data.save()
	return HttpResponseRedirect(reverse('data_desc', kwargs={'dataset_id':dataset_id,'id':id}))

@login_required(login_url='auth_login')
def data_unpublish(request, dataset_id=None, id=None):
	data = Data.objects.filter(id=id)[0]
	data.is_public = False
	data.save()
	return HttpResponseRedirect(reverse('data_edit_desc', kwargs={'dataset_id':dataset_id,'id':id}))

def dataset_desc(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	context = {
		"dataset": dataset,
		"news": news, 		
		"datas": datas,
		"profile": profile_dataset,
	}
	return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))

def dataset_schedule(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	context = {
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule,
		"profile": profile_dataset,
	}
	return render(request, "dataset/schedule.html", context, context_instance=RequestContext(request))

def dataset_associated_events(request, dataset_id=None):
	c = None
	d = None
	w = None
	s = None
	if dataset_id==None:
		if Challenge.objects.filter(id=id).count() > 0:
			c = Challenge.objects.filter(id=id)[0]
		elif Workshop.objects.filter(id=id).count() > 0:
			w = Workshop.objects.filter(id=id)[0]
		elif Special_Issue.objects.filter(id=id).count() > 0:
			s = Special_Issue.objects.filter(id=id)[0]
	else:
		d = Dataset.objects.filter(id=dataset_id)[0]
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	relations = Event_Relation.objects.filter(dataset_associated__id=dataset_id)
	associated = Event_Relation.objects.filter(dataset_relation=dataset)
	news = News.objects.filter(dataset_id=dataset_id)
	profile_dataset = check_dataset_permission(request, dataset)
	context = {
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule,
		"relations": relations,
		"associated": associated,
		"profile": profile_dataset,
		"c": c, 
		"w": w,
		"d": d,
		"s": s,
	}
	return render(request, "dataset/relations.html", context, context_instance=RequestContext(request))

def dataset_publications(request, id=None):
	dataset = Dataset.objects.filter(id=id)[0]
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	publications = Publication.objects.filter(dataset=id)
	context = {
		"dataset": dataset,
		"news": news, 		
		"datas": datas,
		"profile": profile_dataset,
		"publications": publications,
	}
	return render(request, "dataset/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
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
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_creation(request, id=None):
	dataform = DataCreationForm()
	fileform = FileCreationForm()
	dataset = Dataset.objects.filter(id=id)[0]
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
			return HttpResponseRedirect(reverse('dataset_edit_datas', kwargs={'id':id}))
	context = {
		"dataform": dataform,
		"fileform": fileform,
		"dataset_id": id,
		"dataset": dataset,
	}
	return render(request, "data/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_remove(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	data.delete()
	return HttpResponse(reverse('dataset_edit_datas', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_edit(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	files = File.objects.filter(data=data)
	dataform = DataEditForm(data=data)
	dataset = Dataset.objects.filter(id=dataset_id)[0]
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
			return HttpResponseRedirect(reverse('dataset_edit_datas', kwargs={'id':dataset_id}))
	context = {
		"dataform": dataform,
		"data": data,
		"files": files,
		"dataset_id": dataset_id,
		"dataset": dataset,
	}
	return render(request, "data/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_edit_desc(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	dataform = DataEditForm(data=data)
	dataset = Dataset.objects.filter(id=dataset_id)[0]
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
			return HttpResponseRedirect(reverse('data_edit_desc', kwargs={'id':id,'dataset_id':dataset_id}))
	context = {
		"dataform": dataform,
		"data": data,
		"dataset": dataset,
	}
	return render(request, "data/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_edit_files(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	files = File.objects.filter(data=data)
	context = {
		"files": files,
		"data": data,
		"dataset": dataset,
	}
	return render(request, "data/edit/files.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def file_creation(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id)[0]
	dataset = Dataset.objects.filter(id=dataset_id)[0]
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
			return HttpResponseRedirect(reverse('data_edit_files', kwargs={'id':data.id, 'dataset_id': dataset_id}))
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
		"dataset": dataset,
	}
	return render(request, "file/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def file_remove(request, id=None, file_id=None, dataset_id=None):
	new_file = File.objects.filter(id=file_id)[0]
	new_file.delete()
	return HttpResponse(reverse('data_edit_files', kwargs={'id':id, 'dataset_id': dataset_id}))

def data_desc(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/desc.html", context, context_instance=RequestContext(request))

def data_software(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/software.html", context, context_instance=RequestContext(request))

def data_metric(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	data = Data.objects.filter(id=id)[0]
	news = News.objects.filter(dataset=dataset)
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
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
		"files": files,
	}
	return render(request, "data/files.html", context, context_instance=RequestContext(request))

def dataset_results(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	news = News.objects.filter(dataset=dataset)
	submission = Submission.objects.filter(dataset=dataset)
	datas = Data.objects.all().filter(dataset=dataset)
	scores = None
	names = None
	submissions = None
	if submission:
		submission = Submission.objects.filter(dataset=dataset)[0]
		submissions = Submission.objects.filter(dataset=dataset)
		scores = []
		for s in submissions:
			sub_results = Score.objects.filter(submission=s)
			scores.append((s,sub_results))
	names = Col.objects.all().filter(dataset=dataset)
	profile_dataset = check_dataset_permission(request, dataset)
	context = {
		"dataset": dataset,
		"datas": datas,
		"news": news,
		"names": names,	
		"scores": scores,
		"profile": profile_dataset,
	}
	return render(request, "dataset/results.html", context, context_instance=RequestContext(request))

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
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def partner_select(request, id=None):
	c = None
	if Challenge.objects.filter(id=id).count() > 0:
		c = Challenge.objects.filter(id=id)[0]
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
				return HttpResponseRedirect(reverse('challenge_edit_sponsors', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_desc', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"selectform": selectform,
		"selectRoleForm": selectRoleForm,
		"c": c,
	}
	return render(request, "partner/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def event_list(request):
	challenges_list = Challenge.objects.all()
	workshop_list = Workshop.objects.all()
	issues_list = Special_Issue.objects.all()
	context = {
		"challenges_list": challenges_list,
		"workshop_list": workshop_list,
		"issues_list": issues_list,
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
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_remove(request, id=None):
	event = Event.objects.filter(id=id)[0]
	event.delete()
	if request.method == 'POST':
		return HttpResponse((reverse('event_list')))
		# return HttpResponse(reverse('event_list'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_relation_remove(request, id=None, relation_id=None, dataset_id=None):
	relation = Event_Relation.objects.filter(id=relation_id)[0]
	relation.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_relation', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_relations', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_relations', kwargs={'id':id}))
	elif Dataset.objects.filter(id=dataset_id).count() > 0:
		return HttpResponse(reverse('dataset_edit_relations', kwargs={'id':dataset_id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_member_remove(request, id=None, member_id=None):
	profile = Profile_Event.objects.filter(id=member_id)[0]
	profile.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_members', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_members', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_members', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_member_remove(request, dataset_id=None, member_id=None):
	profile = Profile_Dataset.objects.filter(id=member_id)[0]
	profile.delete()
	return HttpResponse(reverse('dataset_edit_members', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_news_remove(request, id=None, news_id=None):
	news = News.objects.filter(id=news_id)[0]
	news.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_news', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_news', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_news', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_news_remove(request, dataset_id=None, news_id=None):
	news = News.objects.filter(id=news_id)[0]
	news.delete()
	return HttpResponse(reverse('dataset_edit_news', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_schedule_remove(request, dataset_id=None, schedule_id=None):
	program = Schedule_Event.objects.filter(id=schedule_id)[0]
	program.delete()
	return HttpResponse(reverse('dataset_edit_schedule', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_program_remove(request, id=None, program_id=None):
	program = Schedule_Event.objects.filter(id=program_id)[0]
	program.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_desc', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_program', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_desc', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_schedule_remove(request, id=None, program_id=None):
	schedule = Schedule_Event.objects.filter(id=program_id)[0]
	schedule.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_schedule', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_schedule', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_schedule', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_partner_remove(request, id=None, partner_id=None):
	partner = Event_Partner.objects.filter(id=partner_id)[0]
	partner.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_sponsors', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_desc', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_desc', kwargs={'id':id}))
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
			profile = Profile.objects.filter(user=request.user)[0]
			Proposal.objects.create(title=title,description=desc,type=event_type,user=profile)
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
def event_proposal_confirm(request, id=None):
	proposal = Proposal.objects.filter(id=id)[0]
	if proposal.type=='1':
		new_challenge = Challenge.objects.create(title=proposal.title, description=proposal.description)
		new_role, created = Role.objects.get_or_create(name='Admin')
		Profile_Event.objects.create(profile=proposal.user,event=new_challenge,role=new_role)
		return HttpResponseRedirect(reverse('challenge_edit_desc', kwargs={'id':new_challenge.id}))
	elif proposal.type=='2':
		new_issue = Special_Issue.objects.create(title=proposal.title, description=proposal.description)
		new_role, created = Role.objects.get_or_create(name='Admin')
		print proposal.user.first_name
		Profile_Event.objects.create(profile=proposal.user,event=new_issue,role=new_role)
		return HttpResponseRedirect(reverse('special_issue_edit_desc', kwargs={'id':new_issue.id}))
	elif proposal.type=='3':
		new_workshop = Workshop.objects.create(title=proposal.title, description=proposal.description)
		new_role, created = Role.objects.get_or_create(name='Admin')
		profile_event = Profile_Event.objects.create(profile=proposal.user,event=new_workshop,role=new_role)
		return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':new_workshop.id}))

@login_required(login_url='auth_login')
def challenge_edit_desc(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:
		eventform = EditEventForm(event=challenge)
		if request.method == 'POST':
			eventform = EditEventForm(request.POST, request.FILES, event=challenge)
			if eventform.is_valid():
				title = eventform.cleaned_data["title"]
				desc = eventform.cleaned_data["description"]
				challenge.title = title
				challenge.description = desc
				challenge.save()
				return HttpResponseRedirect(reverse('challenge_edit_desc', kwargs={'id':challenge.id}))
		context = {
			"eventform": eventform,
			"challenge": challenge, 
			"tracks": tracks,
		}
		return render(request, "challenge/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_schedule(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:
		schedule = Schedule_Event.objects.filter(event_schedule=challenge,schedule_event_parent=None).order_by('date')
		context = {
			"tracks": tracks,
			"challenge": challenge, 
			"schedule": schedule,
		}
		return render(request, "challenge/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_relation(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:
		relations = Event_Relation.objects.filter(event_associated=challenge)
		associated = Event_Relation.objects.filter(challenge_relation=challenge)
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"relations": relations,
			"associated": associated,
		}
		return render(request, "challenge/edit/relation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_result(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		eventform = EditChallengeResult()
		result = Result.objects.filter(challenge=challenge)
		results = None
		scores = None
		names = None
		if result:
			result = Result.objects.filter(challenge=challenge)[0]
			scores = Score.objects.filter(result__challenge=challenge)
			results = Result.objects.filter(challenge=challenge)
			qset = Score.objects.filter(result=result)
			names = []
			for n in qset:
				names.append(n.name)
		if request.method == 'POST':
			eventform = EditChallengeResult(request.POST, request.FILES)
			if eventform.is_valid():
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
				return HttpResponseRedirect(reverse('challenge_edit_result', kwargs={'id':challenge.id}))
		context = {
			"eventform": eventform,
			"challenge": challenge, 
			"results": results,
			"names": names, 
			"scores": scores,
			"tracks": tracks,
		}
		return render(request, "challenge/edit/result.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_members(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		members = []
		roles = Role.objects.all()
		for r in roles:
			members2 = Profile_Event.objects.filter(event=challenge,role=r)
			if members2.count() > 0:
				members.append((r.name,members2))
		context = {
			"challenge": challenge, 
			"members": members,
			"tracks": tracks,
		}
		return render(request, "challenge/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_sponsors(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		partners = Event_Partner.objects.filter(event_id=id)
		context = {
			"challenge": challenge, 
			"partners": partners,
			"tracks": tracks,
		}
		return render(request, "challenge/edit/sponsors.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_tracks(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		context = {
			"challenge": challenge, 
			"tracks": tracks,
		}
		return render(request, "challenge/edit/tracks.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_news(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	news = News.objects.filter(event_id=id)	
	if check_edit_event_permission(request, challenge) == False:
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news
		}
		return render(request, "challenge/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_publications(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge=challenge)
	if check_edit_event_permission(request, challenge) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))
	else:	
		publications = Publication.objects.filter(event=challenge)
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"publications": publications,
		}
		return render(request, "challenge/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_edit(request, id=None, result_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	result = Result.objects.filter(id=result_id)[0]
	resultform = ResultEditForm(result=result)
	if request.method == 'POST':
		resultform = ResultEditForm(request.POST, result=result)
		if resultform.is_valid():
			name = resultform.cleaned_data['name']
			sheets = resultform.cleaned_data['sheets']
			code = resultform.cleaned_data['code']
			website = resultform.cleaned_data['website']
			article = resultform.cleaned_data['article']
			other = resultform.cleaned_data['other']
			result.user = name
			result.sheets = sheets
			result.code = code
			result.website = website
			result.article = article
			result.other = other
			result.save()
	context = {
		"resultform": resultform,
	}
	return render(request, "challenge/edit/result_user.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_remove(request, id=None, result_id=None):
	result = Result.objects.filter(id=result_id)[0]
	result.delete()
	return HttpResponse(reverse('challenge_edit_result', kwargs={'id':id}))

@login_required(login_url='auth_login')
def challenge_publish(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	challenge.is_public = True
	challenge.save()
	return HttpResponseRedirect(reverse('challenge_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def challenge_unpublish(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	challenge.is_public = False
	challenge.save()
	return HttpResponseRedirect(reverse('challenge_edit_desc', kwargs={'id':id}))

def challenge_desc(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"profile": profile_event,
	}
	return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))

def challenge_associated_events(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated=challenge)
	associated = Event_Relation.objects.filter(challenge_relation=challenge)
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"relations": relations,
		"associated": associated,
		"profile": profile_event,		
	}
	return render(request, "challenge/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def event_relation_creation(request, id=None, dataset_id=None):
	c = None
	d = None
	w = None
	s = None
	if dataset_id==None:
		if Challenge.objects.filter(id=id).count() > 0:
			c = Challenge.objects.filter(id=id)[0]
		elif Workshop.objects.filter(id=id).count() > 0:
			w = Workshop.objects.filter(id=id)[0]
		elif Special_Issue.objects.filter(id=id).count() > 0:
			s = Special_Issue.objects.filter(id=id)[0]
	else:
		d = Dataset.objects.filter(id=dataset_id)[0]
	if id==None:
		events = Event.objects.filter(is_public=True)
	else:
		events = Event.objects.filter(is_public=True).exclude(id__in = [id])
	datasets = Dataset.objects.filter(is_public=True)
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
				return HttpResponseRedirect(reverse('challenge_edit_relation', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_relations', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_relations', kwargs={'id':id}))
			elif Dataset.objects.filter(id=dataset_id).count() > 0:
				return HttpResponseRedirect(reverse('dataset_edit_relations', kwargs={'id':dataset_id}))
			else:
				return HttpResponseRedirect(reverse('home'))

	context = {
		"relationform": relationform,
		"c": c, 
		"w": w, 
		"d": d, 
		"s": s,
	}
	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def event_relation_edit(request, id=None, relation_id=None):
	c = None
	d = None
	w = None
	s = None
	if dataset_id==None:
		if Challenge.objects.filter(id=id).count() > 0:
			c = Challenge.objects.filter(id=id)[0]
		elif Workshop.objects.filter(id=id).count() > 0:
			w = Workshop.objects.filter(id=id)[0]
		elif Special_Issue.objects.filter(id=id).count() > 0:
			s = Special_Issue.objects.filter(id=id)[0]
	else:
		d = Dataset.objects.filter(id=dataset_id)[0]
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
		"c": c, 
		"w": w, 
		"d": d, 
		"s": s,
	}
	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

def track_desc(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/desc.html", context, context_instance=RequestContext(request))

def track_metrics(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/metrics.html", context, context_instance=RequestContext(request))

def track_baseline(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id)[0]
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/baseline.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_creation(request, id=None):
	c = None
	if Challenge.objects.filter(id=id).count() > 0:
		c = Challenge.objects.filter(id=id)[0]
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
			return HttpResponseRedirect(reverse('challenge_edit_tracks', kwargs={'id':id}))
	context = {
		"trackform": trackform,
		"c": c,
	}
	return render(request, "track/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_edit(request, id=None, track_id=None):
	c = None
	if Challenge.objects.filter(id=id).count() > 0:
		c = Challenge.objects.filter(id=id)[0]
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
			return HttpResponseRedirect(reverse('challenge_edit_tracks', kwargs={'id':id}))
	context = {
		"trackform": trackform,
		"c": c,
	}
	return render(request, "track/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_remove(request, id=None, track_id=None):
	track = Track.objects.filter(id=track_id)[0]
	track.delete()
	return HttpResponse(reverse('challenge_edit_tracks', kwargs={'id':id}))

def challenge_members(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	members = []
	roles = Role.objects.all()
	for r in roles:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			members.append((r.name,members2))
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"members": members,
		"news": news,
		"tracks": tracks,		
		"profile": profile_event,		
	}
	return render(request, "challenge/members.html", context, context_instance=RequestContext(request))

def challenge_sponsors(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	sponsors = Event_Partner.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"sponsors": sponsors,
		"news": news,
		"tracks": tracks,
		"profile": profile_event,		
	}
	return render(request, "challenge/sponsors.html", context, context_instance=RequestContext(request))

def challenge_schedule(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=challenge,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"schedule": schedule,
		"tracks": tracks,	
		"profile": profile_event,					
	}
	return render(request, "challenge/schedule.html", context, context_instance=RequestContext(request))

def challenge_result(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	result = Result.objects.filter(challenge=challenge)
	results = None
	scores = None
	names = None
	if result:
		result = Result.objects.filter(challenge=challenge)[0]
		scores = Score.objects.filter(result__challenge=challenge)
		results = Result.objects.filter(challenge=challenge)
		qset = Score.objects.filter(result=result)
		names = []
		for n in qset:
			names.append(n.name)
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"scores": scores,	
		"names": names,	
		"results": results,
		"profile": profile_event,		
	}
	return render(request, "challenge/result.html", context, context_instance=RequestContext(request))

def challenge_publications(request, id=None):
	challenge = Challenge.objects.filter(id=id)[0]
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	publications = Publication.objects.filter(event=id)
	profile_event = check_event_permission(request, challenge)
	context = {
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"publications": publications,
		"profile": profile_event,		
	}
	return render(request, "challenge/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=workshop, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=workshop, profile=profile)[0]
			if not profile_event.is_admin():
				return HttpResponseRedirect(reverse('home'))
		else:
			return HttpResponseRedirect(reverse('home'))
	profile_event = check_event_permission(request, workshop)
	members = Profile_Event.objects.filter(event=workshop)
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
		"members": members,
		"workshop": workshop,
		"program": program,
		"news": news,
		"images": images, 
		"schedule": schedule,
		"relations": relations,
		"profile": profile_event,
	}
	return render(request, "workshop/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_desc(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		eventform = EditEventForm(event=workshop)
		if request.method == 'POST':
			eventform = EditEventForm(request.POST, event=workshop)
			if eventform.is_valid():
				title = eventform.cleaned_data["title"]
				desc = eventform.cleaned_data["description"]
				workshop.title = title
				workshop.description = desc
				workshop.save()
				return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':id}))
		context = {
			"eventform": eventform,
			"workshop": workshop,
		}
		return render(request, "workshop/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_schedule(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		schedule = Schedule_Event.objects.filter(event_schedule=workshop,schedule_event_parent=None).order_by('date')
		context = {
			"workshop": workshop,
			"schedule": schedule,
		}
		return render(request, "workshop/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_relations(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:	
		relations = Event_Relation.objects.filter(event_associated=workshop)
		associated = Event_Relation.objects.filter(workshop_relation=workshop)
		context = {
			"relations": relations,
			"workshop": workshop,
			"associated": associated,
		}
		return render(request, "workshop/edit/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_program(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		program = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
		context = {
			"program": program,
			"workshop": workshop,
		}
		return render(request, "workshop/edit/program.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_members(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		members = []
		roles = Role.objects.all()
		for r in roles:
			members2 = Profile_Event.objects.filter(event=workshop,role=r)
			if members2.count() > 0:
				members.append((r.name,members2))
		context = {
			"members": members,
			"workshop": workshop,
		}
		return render(request, "workshop/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_gallery(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		images = Gallery_Image.objects.filter(workshop=workshop)
		context = {
			"images": images,
			"workshop": workshop,
		}
		return render(request, "workshop/edit/gallery.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_news(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	if check_edit_event_permission(request, workshop) == False:
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		context = {
			"news": news,
			"workshop": workshop,
		}
		return render(request, "workshop/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_publications(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	if check_edit_event_permission(request, workshop) == False:
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication.objects.filter(event=id)
		context = {
			"workshop": workshop,
			"news": news,
			"publications": publications,
		}
		return render(request, "workshop/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_publish(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	workshop.is_public = True
	workshop.save()
	return HttpResponseRedirect(reverse('workshop_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def workshop_unpublish(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	workshop.is_public = False
	workshop.save()
	return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':id}))

def workshop_desc(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"profile": profile_event,				
	}
	return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))

def workshop_schedule(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=workshop,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"schedule": schedule,
		"profile": profile_event,
	}
	return render(request, "workshop/schedule.html", context, context_instance=RequestContext(request))

def workshop_associated_events(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(workshop_relation=workshop)
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"relations": relations,
		"associated": associated,
		"profile": profile_event,
	}
	return render(request, "workshop/relation.html", context, context_instance=RequestContext(request))

def workshop_program(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	program = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"program": program,
		"profile": profile_event,
	}
	return render(request, "workshop/program.html", context, context_instance=RequestContext(request))

def workshop_speakers(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	speakers = Profile_Event.objects.filter(role__name='speaker', event=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"speakers": speakers,
		"news": news,
		"profile": profile_event,
	}
	return render(request, "workshop/speakers.html", context, context_instance=RequestContext(request))

def workshop_gallery(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	images = Gallery_Image.objects.filter(workshop=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	context = {
		"workshop": workshop,
		"news": news,
		"images": images,
		"profile": profile_event,
	}
	return render(request, "workshop/gallery.html", context, context_instance=RequestContext(request))

def workshop_publications(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication.objects.filter(event=id)
	context = {
		"workshop": workshop,
		"news": news,
		"publications": publications,
		"profile": profile_event,
	}
	return render(request, "workshop/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def add_gallery_picture(request, id=None):
	workshop = Workshop.objects.filter(id=id)[0]
	form = GalleryImageForm()
	if request.method == 'POST':
		form = GalleryImageForm(request.POST, request.FILES)
		if form.is_valid():
			image = form.cleaned_data["image"]
			desc = form.cleaned_data["desc"]
			Gallery_Image.objects.create(image=image, description=desc, workshop=workshop)
			return HttpResponseRedirect(reverse('workshop_edit_gallery', kwargs={'id':id}))
	context = {
		"workshop": workshop,
		"form": form,
	}
	return render(request, "workshop/add_picture.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def remove_gallery_picture(request, id=None, pic_id=None):
	image = Gallery_Image.objects.filter(id=pic_id)
	image.delete()
	return HttpResponse(reverse('workshop_edit_gallery', kwargs={'id':id}))

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
			return HttpResponseRedirect(reverse('workshop_edit_members', kwargs={'id':id}))
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

@login_required(login_url='auth_login')
def special_issue_edit(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=issue, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=issue, profile=profile)[0]
			if not profile_event.is_admin():
				return HttpResponseRedirect(reverse('home'))
		else:
			return HttpResponseRedirect(reverse('home'))
	profile_event = None
	if request.user and (not request.user.is_anonymous()):
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=issue, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=issue, profile=profile)[0]
			if not profile_event.is_admin():
				profile_event = None
		else:
			profile_event = None
	news = News.objects.filter(event_id=id)
	members = Profile_Event.objects.filter(event=issue)
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
		"profile": profile_event,
	}
	return render(request, "special_issue/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_desc(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
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
		}
		return render(request, "special_issue/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_relations(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		relations = Event_Relation.objects.filter(event_associated=issue)
		associated = Event_Relation.objects.filter(issue_relation=issue)
		context = {
			"relations": relations,
			"associated": associated,
			"issue": issue,
		}
		return render(request, "special_issue/edit/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_members(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		members = []
		roles = Role.objects.all()
		for r in roles:
			members2 = Profile_Event.objects.filter(event=issue,role=r)
			if members2.count() > 0:
				members.append((r.name,members2))
		context = {
			"members": members,
			"issue": issue,
		}
		return render(request, "special_issue/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_schedule(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
		context = {
			"schedule": schedule,
			"issue": issue,
		}
		return render(request, "special_issue/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_news(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		news = News.objects.filter(event_id=id)
		context = {
			"news": news,
			"issue": issue,
		}
		return render(request, "special_issue/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit_publications(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication.objects.filter(event=id)
		context = {
			"issue": issue,
			"publications": publications,
		}
		return render(request, "special_issue/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_publish(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	issue.is_public = True
	issue.save()
	return HttpResponseRedirect(reverse('special_issue_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def special_issue_unpublish(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	issue.is_public = False
	issue.save()
	return HttpResponseRedirect(reverse('special_issue_edit_desc', kwargs={'id':id}))

def special_issue_desc(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, issue)
	context = {
		"issue": issue,
		"news": news,
		"profile": profile_event,		
	}
	return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))

def special_issue_members(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	members = []
	roles = Role.objects.all()
	for r in roles:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			members.append((r.name,members2))
	profile_event = check_event_permission(request, issue)
	context = {
		"issue": issue,
		"news": news,
		"members": members,
		"profile": profile_event,	
	}
	return render(request, "special_issue/members.html", context, context_instance=RequestContext(request))

def special_issue_schedule(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, issue)
	context = {
		"issue": issue,
		"news": news,
		"schedule": schedule,
		"profile": profile_event,	
	}
	return render(request, "special_issue/schedule.html", context, context_instance=RequestContext(request))

def special_issue_associated_events(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(issue_relation=issue)
	profile_event = check_event_permission(request, issue)
	context = {
		"issue": issue,
		"news": news,
		"relations": relations,
		"associated": associated,
		"profile": profile_event,	
	}
	return render(request, "special_issue/relations.html", context, context_instance=RequestContext(request))

def special_issue_publications(request, id=None):
	issue = Special_Issue.objects.filter(id=id)[0]
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(event=id)
	context = {
		"issue": issue,
		"news": news,
		"profile": profile_event,
		"publications": publications,
	}
	return render(request, "special_issue/publications.html", context, context_instance=RequestContext(request))
	
@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
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
def news_creation(request, id=None, dataset_id=None):
	c = None
	d = None
	w = None
	s = None
	if dataset_id==None:
		if Challenge.objects.filter(id=id).count() > 0:
			c = Challenge.objects.filter(id=id)[0]
		elif Workshop.objects.filter(id=id).count() > 0:
			w = Workshop.objects.filter(id=id)[0]
		elif Special_Issue.objects.filter(id=id).count() > 0:
			s = Special_Issue.objects.filter(id=id)[0]
	else:
		d = Dataset.objects.filter(id=dataset_id)[0]
	if dataset_id == None:
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
					return HttpResponseRedirect(reverse('challenge_edit_news', kwargs={'id':id}))
				elif Workshop.objects.filter(id=id).count() > 0:
					return HttpResponseRedirect(reverse('workshop_edit_news', kwargs={'id':id}))
				elif Special_Issue.objects.filter(id=id).count() > 0:
					return HttpResponseRedirect(reverse('special_issue_edit_news', kwargs={'id':id}))
				else:
					return HttpResponseRedirect(reverse('home'))
	else:
		dataset = Dataset.objects.filter(id=dataset_id)[0]
		newsform = NewsCreationForm()
		if request.method == 'POST':
			newsform = NewsCreationForm(request.POST)
			if newsform.is_valid():
				title = newsform.cleaned_data['title']
				desc = newsform.cleaned_data['description']
				news = News(title=title,description=desc,dataset=dataset)
				news.save()
				return HttpResponseRedirect(reverse('dataset_edit_news', kwargs={'id':dataset_id}))
	context = {
		"newsform": newsform,
		"c": c,
		"w": w,
		"s": s,
		"d": d,
	}
	return render(request, "news/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def news_edit(request, id=None, news_id=None):
	news = News.objects.filter(id=news_id)[0]
	newsform = NewsEditForm(news=news)
	if request.method == 'POST':
		newsform = NewsEditForm(request.POST, news=news)
		if newsform.is_valid():
			title = newsform.cleaned_data['title']
			desc = newsform.cleaned_data['description']
			news.title = title
			news.description = desc
			news.save()
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit_news', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_news', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_news', kwargs={'id':id}))
			elif Dataset.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('dataset_edit_news', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"newsform": newsform,
	}
	return render(request, "news/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_creation(request, dataset_id=None, event_id=None):
	scheduleform = ScheduleCreationForm()
	c = None
	d = None
	w = None
	s = None
	if dataset_id==None:
		if Challenge.objects.filter(id=event_id).count() > 0:
			c = Challenge.objects.filter(id=event_id)[0]
		elif Workshop.objects.filter(id=event_id).count() > 0:
			w = Workshop.objects.filter(id=event_id)[0]
		elif Special_Issue.objects.filter(id=event_id).count() > 0:
			s = Special_Issue.objects.filter(id=event_id)[0]
	else:
		d = Dataset.objects.filter(id=dataset_id)[0]
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
					return HttpResponseRedirect(reverse('challenge_edit_schedule', kwargs={'id':event_id}))
				elif Workshop.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('workshop_edit_schedule', kwargs={'id':event_id}))
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					return HttpResponseRedirect(reverse('special_issue_edit_schedule', kwargs={'id':event_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
			else:
				dataset = Dataset.objects.filter(id=dataset_id)[0]
				new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,dataset_schedule=dataset)
				if Dataset.objects.filter(id=dataset_id).count() > 0:
					return HttpResponseRedirect(reverse('dataset_edit_schedule', kwargs={'id':dataset_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
	context = {
		"scheduleform": scheduleform,
		"c": c, 
		"d": d, 
		"w": w,
		"s": s,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def program_creation(request, id=None):
	event = Event.objects.filter(id=id)[0]
	w = Workshop.objects.filter(id=id)[0]
	scheduleform = ScheduleCreationForm()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,event_program=event)
			return HttpResponseRedirect(reverse('workshop_edit_program', kwargs={'id':id}))
			# if 'save' in request.POST:
			# 	return HttpResponseRedirect(reverse('home'))
			# elif 'save_continue' in request.POST:
			# 	return HttpResponseRedirect(reverse('subevent_creation', kwargs={'event_id':id,'program_id':new_event.id}))
	context = {
		"scheduleform": scheduleform,
		"w": w,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_edit(request, schedule_id=None, dataset_id=None, event_id=None, program_id=None):
	if program_id==None:
		# event = Event.objects.filter(id=id)[0]
		schedule = Schedule_Event.objects.filter(id=schedule_id)[0]
		scheduleform = ScheduleEditForm(schedule=schedule)
		# subevents = Schedule_Event.objects.filter(schedule_event_parent=schedule).order_by('date')
		c = None
		d = None
		w = None
		s = None
		if dataset_id==None:
			if Challenge.objects.filter(id=event_id).count() > 0:
				c = Challenge.objects.filter(id=event_id)[0]
			elif Workshop.objects.filter(id=event_id).count() > 0:
				w = Workshop.objects.filter(id=event_id)[0]
			elif Special_Issue.objects.filter(id=event_id).count() > 0:
				s = Special_Issue.objects.filter(id=event_id)[0]
		else:
			d = Dataset.objects.filter(id=dataset_id)[0]
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
						return HttpResponseRedirect(reverse('dataset_edit_schedule', kwargs={'id':dataset_id}))
					else:
						return HttpResponseRedirect(reverse('home'))
				else:
					if Challenge.objects.filter(id=event_id).count() > 0:
						return HttpResponseRedirect(reverse('challenge_edit_schedule', kwargs={'id':event_id}))
					elif Workshop.objects.filter(id=event_id).count() > 0:
						return HttpResponseRedirect(reverse('workshop_edit_schedule', kwargs={'id':event_id}))
					elif Special_Issue.objects.filter(id=event_id).count() > 0:
						return HttpResponseRedirect(reverse('special_issue_edit_schedule', kwargs={'id':event_id}))
					else:
						return HttpResponseRedirect(reverse('home'))
		context = {
			"scheduleform": scheduleform,
			# "event": event,
			"schedule": schedule,
			# "subevents": subevents,
			"c": c, 
			"d": d, 
			"w": w,
			"s": s,
		}
	else:
		schedule = Schedule_Event.objects.filter(id=program_id)[0]
		w = Workshop.objects.filter(id=event_id)[0]
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
				return HttpResponseRedirect(reverse('workshop_edit_program', kwargs={'id':event_id}))
		context = {
			"scheduleform": scheduleform,
			"schedule": schedule,
			"w": w,
		}
	return render(request, "program/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
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

@login_required(login_url='auth_login')
def submission_creation(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id)[0]
	results = Col.objects.filter(dataset=dataset)
	form = SubmissionCreationForm()
	scoresform = SubmissionScoresForm(results=results)
	if request.method == 'POST':
		form = SubmissionCreationForm(request.POST, request.FILES)
		scoresform = SubmissionScoresForm(request.POST, results=results)
		if form.is_valid() and scoresform.is_valid():
			source_code = form.cleaned_data['source_code']
			publication = form.cleaned_data['publication']
			sub_file = form.cleaned_data['sub_file']
			if sub_file:
				new_submission = Submission.objects.create(source_code=source_code, publication=publication, sub_file=sub_file, user=request.user, dataset=dataset)
			else:
				new_submission = Submission.objects.create(source_code=source_code, publication=publication, user=request.user, dataset=dataset)
			for r in results: 
				new_score = scoresform.cleaned_data[r.name]
				Score.objects.create(score=new_score, name=r.name, submission=new_submission)
			return HttpResponseRedirect(reverse('dataset_results', kwargs={'dataset_id':dataset_id}))
	context = {
		"form": form,
		"scoresform": scoresform,
	}
	return render(request, "dataset/submission.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def publication_creation(request, id=None):
	# If it creates by challenge, workshop, special issue, dataset edit mode.
	if id==None:
		choices = []
		events = Event.objects.filter(is_public=True)
		datasets = Dataset.objects.filter(is_public=True)
		for e in events:
			choices.append((e.id, e.title))
		for d in datasets:
			choices.append((d.id, d.title))
		form = PublicationCreationForm(choices)
		if request.method == 'POST':
			form = PublicationCreationForm(choices, request.POST)
			if form.is_valid():
				title = form.cleaned_data['title']
				content = form.cleaned_data['content']
				url = form.cleaned_data['url']
				event = form.cleaned_data['event']
				if Event.objects.filter(id=event):
					e = Event.objects.filter(id=event)[0]
					Publication.objects.create(title=title, content=content, url=url, event=e)
				elif Dataset.objects.filter(id=event):
					d = Dataset.objects.filter(id=event)[0]
					Publication.objects.create(title=title, content=content, url=url, dataset=d)
				return HttpResponseRedirect(reverse('publication_list'))
	# If it creates by the global publications list
	else:
		form = PublicationEventCreationForm()
		if request.method == 'POST':
			form = PublicationEventCreationForm(request.POST)
			if form.is_valid():
				title = form.cleaned_data['title']
				content = form.cleaned_data['content']
				url = form.cleaned_data['url']
				if Event.objects.filter(id=id):
					e = Event.objects.filter(id=id)[0]
					Publication.objects.create(title=title, content=content, url=url, event=e)
					if Challenge.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('challenge_edit_publications', kwargs={'id':id}))
					elif Workshop.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('workshop_edit_publications', kwargs={'id':id}))
					elif Special_Issue.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('special_issue_edit_publications', kwargs={'id':id}))
				elif Dataset.objects.filter(id=id):
					d = Dataset.objects.filter(id=id)[0]
					Publication.objects.create(title=title, content=content, url=url, dataset=d)
					return HttpResponseRedirect(reverse('dataset_edit_publications', kwargs={'id':id}))
	context = {
		"form": form,
	}
	return render(request, "publication/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def publication_edit(request, id=None, pub_id=None):
	publication = Publication.objects.filter(id=pub_id)[0]
	form = PublicationEditForm(publication)
	if request.method == 'POST':
		form = PublicationEditForm(publication, request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			url = form.cleaned_data['url']
			publication.title = title
			publication.content = content
			publication.url = url
			publication.save()
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit_publications', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_publications', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_publications', kwargs={'id':id}))
			elif Dataset.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('dataset_edit_publications', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('publication_detail', kwargs={'id':pub_id}))
	context = {
		"form": form,
	}
	return render(request, "publication/edit.html", context, context_instance=RequestContext(request))

def publication_list(request):
	publications = Publication.objects.all()
	if check_staff_user(request):
		context = {
			"publications": publications,
			"perm": True,
		}
	else:
		context = {
			"publications": publications,
		}
	return render(request, "publication/list.html", context, context_instance=RequestContext(request))

def publication_detail(request, id=None):
	publication = Publication.objects.filter(id=id)[0]
	context = {
		"publication": publication,
	}
	return render(request, "publication/detail.html", context, context_instance=RequestContext(request))

def publication_remove(request, id=None, pub_id=None):
	publication = Publication.objects.filter(id=pub_id)[0]
	publication.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_publications', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_publications', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('special_issue_edit_publications', kwargs={'id':id}))
	elif Dataset.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('dataset_edit_publications', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('publication_list'))

def event_detail(request, id=None):
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('challenge_desc', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('workshop_desc', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('special_issue_desc', kwargs={'id':id}))

def check_event_permission(request, event):
	profile_event = None
	if request.user and (not request.user.is_anonymous()):
		if request.user.is_superuser or request.user.is_staff:
			profile_event = Profile.objects.filter(user=request.user)
		else:
			profile = Profile.objects.filter(user=request.user)
			profile_event = Profile_Event.objects.filter(event=event, profile=profile)
			if len(profile_event) > 0:
				profile_event = Profile_Event.objects.filter(event=event, profile=profile)[0]
				if not profile_event.is_admin():
					profile_event = None
			else:
				profile_event = None
	return profile_event

def check_edit_event_permission(request, event):
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=event, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=event, profile=profile)[0]
			if not profile_event.is_admin():
				return False
		else:
			return False

def check_dataset_permission(request, dataset):
	profile_dataset = None
	if request.user and (not request.user.is_anonymous()):
		if request.user.is_superuser or request.user.is_staff:
			profile_dataset = Profile.objects.filter(user=request.user)
		else:
			profile = Profile.objects.filter(user=request.user)
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
			if len(profile_dataset) > 0:
				profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)[0]
				if not profile_dataset.is_admin():
					profile_dataset = None
			else:
				profile_dataset = None
	return profile_dataset

def check_edit_dataset_permission(request, dataset):
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
		if len(profile_dataset) > 0:
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)[0]
			if not profile_dataset.is_admin():
				return False
		else:
			return False

def check_staff_user(request):
	if request.user.is_staff or request.user.is_superuser:
		return True
	else:
		return False