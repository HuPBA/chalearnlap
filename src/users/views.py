from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse
from .forms import CIMLBookForm, EditHomeForm, ResultRowEditForm, ResultRowForm, HeaderEditForm, ResultNewTableForm, GalleryImageEditForm, ResultUserEditForm, ResultUserCreationForm, ProgramEditForm, ProgramCreationForm, PublicationEditForm, PublicationEventCreationForm, PublicationCreationForm, SubmissionEditForm, ColEditForm, EditChallengeResult, ProfileForm, AffiliationForm, SelectRoleForm, UserEditForm, UserRegisterForm, EditProfileForm, EditExtraForm, DatasetCreationForm, DataCreationForm, EventCreationForm, EditEventForm, RoleCreationForm, NewsCreationForm, FileCreationForm, NewsEditForm, SelectDatasetForm, MemberCreationForm, MemberSelectForm, PartnerCreationForm, PartnerSelectForm, ScheduleCreationForm, ScheduleEditForm, DatasetEditForm, DataEditForm, TrackCreationForm, GalleryImageForm, TrackEditForm, RelationCreationForm, RelationEditForm, SubmissionCreationForm, SubmissionScoresForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CIMLBook, Chalearn, Result_Grid, Grid_Header, Result_User, Publication_Event, Publication_Dataset, Publication, Profile_Dataset, Submission, Profile, Result, Score, Proposal, Profile_Event, Affiliation, Event, Dataset, Data, Partner, Event, Special_Issue, Workshop, Challenge, Role, News, File, Contact, Event_Partner, Schedule_Event, Track, Gallery_Image, Event_Relation
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
from itertools import chain
from django.forms import modelformset_factory

@require_POST
def file_upload(request):
	file_id = request.POST.get('file_id', '')
	file = upload_receive(request)
	new_file = File.objects.filter(id=file_id).first()
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

@require_POST
def image_upload(request):
	workshop_id = request.POST.get('workshop_id', '')
	workshop = Workshop.objects.filter(id=workshop_id).first()
	image = upload_receive(request)
	new_image = Gallery_Image.objects.create(image=image, workshop=workshop)
	basename = new_image.image.name
	file_dict = {
		'name' : basename,
		'size' : image.size,
		'url': settings.MEDIA_URL + basename,
		'thumbnailUrl': settings.MEDIA_URL + basename,
	}
	return UploadResponse(request, file_dict)

class Backend(RegistrationView):
	def register(self, form):
		email = form.cleaned_data["email"]
		# password = User.objects.make_random_password()
		password = 'chalearn'
		username = email.split("@").first()
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
	chalearn = Chalearn.objects.filter(id=1).first()
	return render(request, "home.html", {"news": news, "chalearn": chalearn}, context_instance=RequestContext(request))

def home_edit(request):
	chalearn = Chalearn.objects.filter(id=1).first()
	form = EditHomeForm(chalearn=chalearn)
	if request.method == 'POST':
		form = EditHomeForm(request.POST, chalearn=chalearn)
		if form.is_valid():
			chalearn.home_text = form.cleaned_data['text']
			chalearn.save()
			return HttpResponseRedirect(reverse('home'))
	return render(request, "home-edit.html", {"chalearn": chalearn, "form": form}, context_instance=RequestContext(request))

def cimlbook_detail(request, id=None):
	book = CIMLBook.objects.filter(id=id).first()
	news = News.objects.order_by('-upload_date')[:5]
	profile = None
	if request.user and (not request.user.is_anonymous()):
		if request.user.is_superuser or request.user.is_staff:
			profile = Profile.objects.filter(user=request.user)
	return render(request, "cimlbook-detail.html", {"book": book, "news": news, "profile": profile}, context_instance=RequestContext(request))

def cimlbook_creation(request):
	form = CIMLBookForm()
	if request.method == 'POST':
		form = CIMLBookForm(request.POST)
		if form.is_valid():
			CIMLBook.objects.create(name=form.cleaned_data['name'], content=form.cleaned_data['content'])
			return HttpResponseRedirect(reverse('home'))
	return render(request, "cimlbook-edit.html", {"form": form}, context_instance=RequestContext(request))

def cimlbook_edit(request, id=None):
	book = CIMLBook.objects.filter(id=id).first()
	form = CIMLBookForm(book=book)
	if request.method == 'POST':
		form = CIMLBookForm(request.POST, book=book)
		if form.is_valid():
			book.name = form.cleaned_data['name']
			book.content = form.cleaned_data['content']
			book.save()
			return HttpResponseRedirect(reverse('cimlbook_detail', kwargs={'id':id}))
	return render(request, "cimlbook-edit.html", {"form": form}, context_instance=RequestContext(request))

def cimlbook_remove(request, id=None):
	book = CIMLBook.objects.filter(id=id).first()
	book.delete()
	return HttpResponse(reverse('home'))

def main_organizers(request):
	profiles = Profile.objects.filter(main_org=True)
	return render(request, "main-organizers.html", {"profiles": profiles}, context_instance=RequestContext(request))

def handler404(request):
	response = render_to_response('404.html', {}, context_instance=RequestContext(request))
	response.status_code = 404
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def user_list(request):
	users = User.objects.all().filter(is_staff=False)
	admins = User.objects.all().filter(is_staff=True)
	profiles = Profile.objects.all()
	context = {
		"profiles": profiles,
		"users": users,
		"admins": admins,
	}
	return render(request, "user/list.html", context, context_instance=RequestContext(request));

@login_required(login_url='auth_login')
def user_edit(request, id=None):
	profile = Profile.objects.filter(user__id=id).first()
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
			profile.newsletter = form.cleaned_data["newsletter"] 
			profile.affiliation = affiliation
			profile.save()
			return HttpResponseRedirect(reverse('home'))
	context = {
		"form": form,
		"user_edit": user.id,
	}
	return render(request, "user/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_user_csv(request):
	users = Profile.objects.all()
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="all-users.csv"'
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
		if u.user:
			writer.writerow([u.pk,unicode(u.user.username),unicode(u.first_name).encode('utf-8'),unicode(u.last_name).encode('utf-8'),unicode(u.user.email).encode('utf-8'),(u.affiliation),events])
		else: 
			writer.writerow([u.pk,'',unicode(u.first_name).encode('utf-8'),unicode(u.last_name).encode('utf-8'),unicode(u.email).encode('utf-8'),(u.affiliation),events])
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_members_csv(request, event_id=None):
	event = Event.objects.filter(id=event_id).first()
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
		if u.user:
			writer.writerow([u.pk,unicode(u.user.username),unicode(u.first_name).encode('utf-8'),unicode(u.last_name).encode('utf-8'),unicode(u.user.email).encode('utf-8'),(u.affiliation),unicode(role_name).encode('utf-8')])
		else: 
			writer.writerow([u.pk,'',unicode(u.first_name).encode('utf-8'),unicode(u.last_name).encode('utf-8'),unicode(u.email).encode('utf-8'),(u.affiliation),unicode(role_name).encode('utf-8')])
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_participants_csv(request, dataset_id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	grid = Result_Grid.objects.filter(id=grid_id).first()
	submissions = Submission.objects.filter(grid=grid)
	response = HttpResponse(content_type='text/csv')
	filename = (dataset.title).replace(" ", "-")+'_participants.csv'
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	writer = csv.writer(response)
	response.write(u'\ufeff'.encode('utf8'))
	writer.writerow(['ID','Username','First name','Last name','Email','Affiliation'])
	for u in submissions:
		u = Profile.objects.filter(user=u.user).first()
		writer.writerow([u.pk,unicode(u.user.username),unicode(u.first_name).encode('utf-8'),unicode(u.last_name).encode('utf-8'),unicode(u.user.email).encode('utf-8'),(u.affiliation)])
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_user_xls(request):
	users = Profile.objects.all()
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="all-users.xls"'

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
		if u.user:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff,events]
		else:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,'',u.first_name,u.last_name,u.email,aff,events]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.save(response)
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_members_xls(request, event_id=None):
	event = Event.objects.filter(id=event_id).first()
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
		if u.user:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff,role_name]
		else:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,'',u.first_name,u.last_name,u.email,aff,role_name]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.save(response)
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_participants_xls(request, dataset_id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	grid = Result_Grid.objects.filter(id=grid_id).first()
	submissions = Submission.objects.filter(grid=grid)
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
		u = Profile.objects.filter(user=u.user).first()
		row_num += 1
		if u.affiliation.name and u.affiliation.country and u.affiliation.city:
			aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
		elif u.affiliation.name and u.affiliation.country:
			aff = u.affiliation.name+str(', ')+u.affiliation.country
		elif u.affiliation.name and u.affiliation.city:
			aff = u.affiliation.name+str(', ')+u.affiliation.city
		elif u.affiliation.name:
			aff = u.affiliation.name
		else:
			aff = ''
		row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff]
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
		if u.user:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff,events]
		else:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,'',u.first_name,u.last_name,u.email,aff,events]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.close()
	output.seek(0)
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename="all-users.xlsx"'
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_members_xlsx(request, event_id=None):
	event = Event.objects.filter(id=event_id).first()
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
		if u.user:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff,role_name]
		else:
			if u.affiliation.name and u.affiliation.country and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.country:
				aff = u.affiliation.name+str(', ')+u.affiliation.country
			elif u.affiliation.name and u.affiliation.city:
				aff = u.affiliation.name+str(', ')+u.affiliation.city
			elif u.affiliation.name:
				aff = u.affiliation.name
			else:
				aff = ''
			row=[u.pk,'',u.first_name,u.last_name,u.email,aff,role_name]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])
	workbook.close()
	output.seek(0)
	filename = (event.title).replace(" ", "-")+'_members.xlsx'
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_superuser, login_url='/')
def export_participants_xlsx(request, dataset_id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	grid = Result_Grid.objects.filter(id=grid_id).first()
	submissions = Submission.objects.filter(grid=grid)
	output = StringIO.StringIO()
	workbook = xlsxwriter.Workbook(output)
	worksheet = workbook.add_worksheet('Dataset participants')
	row_num = 0
	columns = ['ID','Username','First name','Last name','Email','Affiliation']
	for col_num in range(len(columns)):
		worksheet.write(row_num, col_num, columns[col_num])  

	for u in submissions:
		u = Profile.objects.filter(user=u.user).first()
		row_num += 1
		if u.affiliation.name and u.affiliation.country and u.affiliation.city:
			aff = u.affiliation.name+str(', ')+u.affiliation.city+str(', ')+u.affiliation.country
		elif u.affiliation.name and u.affiliation.country:
			aff = u.affiliation.name+str(', ')+u.affiliation.country
		elif u.affiliation.name and u.affiliation.city:
			aff = u.affiliation.name+str(', ')+u.affiliation.city
		elif u.affiliation.name:
			aff = u.affiliation.name
		else:
			aff = ''
		row=[u.pk,u.user.username,u.first_name,u.last_name,u.user.email,aff]
		for col_num in range(len(row)):
			worksheet.write(row_num, col_num, row[col_num])

	workbook.close()
	output.seek(0)
	filename = (dataset.title).replace(" ", "-")+'_participants.xlsx'
	response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  
	response['Content-Disposition'] = 'attachment; filename=%s' % filename

	return response

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def profile_edit(request, id=None, member_id=None):
	profile = Profile.objects.filter(id=member_id).first()
	event = Event.objects.filter(id=id).first()
	affiliation = profile.affiliation
	form = EditExtraForm(profile=profile, affiliation=affiliation)
	if request.method == 'POST':
		form = EditExtraForm(request.POST, request.FILES, profile=profile, affiliation=affiliation)
		if form.is_valid():
			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["last_name"]
			avatar = form.cleaned_data["avatar"]
			bio = form.cleaned_data["bio"]
			name = form.cleaned_data["name"]
			country = form.cleaned_data["country"]
			city = form.cleaned_data["city"]
			email = form.cleaned_data["email"]
			profile.newsletter = form.cleaned_data["newsletter"]
			affiliation.name = name
			affiliation.country = country
			affiliation.city = city
			affiliation.save()
			profile.affiliation = affiliation
			profile.first_name = first_name
			profile.last_name = last_name
			profile.avatar = avatar
			profile.bio = bio
			profile.email = email
			if form.cleaned_data["main_org"] == 'True':
				profile.main_org = True
			elif form.cleaned_data["main_org"] == 'False':
				profile.main_org = False
			profile.save()
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit_members', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_members', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_edit_members', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('user_list'))
	context = {
		"form": form,
		"event": event,
	}
	return render(request, "profile/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def profile_creation(request, id=None):
	form = EditExtraForm()
	event = Event.objects.filter(id=id).first()
	if request.method == 'POST':
		form = EditExtraForm(request.POST, request.FILES)
		if form.is_valid():
			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["last_name"]
			avatar = form.cleaned_data["avatar"]
			bio = form.cleaned_data["bio"]
			name = form.cleaned_data["name"]
			country = form.cleaned_data["country"]
			city = form.cleaned_data["city"]
			email = form.cleaned_data["email"]
			new_aff = Affiliation.objects.create(name=name, country=country, city=city)
			if form.cleaned_data["main_org"] == 'True':
				Profile.objects.create(affiliation=new_aff, first_name=first_name, last_name=last_name, avatar=avatar, bio=bio, email=email, main_org=True)
			elif form.cleaned_data["main_org"] == 'False':
				Profile.objects.create(affiliation=new_aff, first_name=first_name, last_name=last_name, avatar=avatar, bio=bio, email=email, main_org=False)
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_profile_select', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_profile_select', kwargs={'id':id}))
			elif Special_Issue.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('special_issue_profile_select', kwargs={'id':id}))
	context = {
		"form": form,
		"event": event,
	}
	return render(request, "profile/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@csrf_protect
def profile_select(request, id=None):
	choices = []
	event = Event.objects.filter(id=id).first()
	roles = Role.objects.all()
	for r in roles:
	    choices.append((r.id, r.name))
	profile_events = Profile_Event.objects.filter(event_id=id)
	qset = Profile.objects.all()
	selectRoleForm = SelectRoleForm(choices)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectRoleForm = SelectRoleForm(choices, request.POST)
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectRoleForm.is_valid() and selectform.is_valid():
			members = selectform.cleaned_data['email']
			role = Role.objects.filter(id=selectRoleForm.cleaned_data["role_select"]).first()
			for m in members:
				profile = Profile.objects.filter(id=m.id).first()
				new_profile_event = Profile_Event.objects.create(profile=profile, event=event, role=role)
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
		"event": event,
	}
	return render(request, "profile/select.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@csrf_protect
def dataset_profile_select(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	profile_dataset = Profile_Dataset.objects.filter(dataset=dataset)
	ids = []
	for p in profile_dataset:
		if p.role.name.lower() == 'admin':
			ids.append(p.profile.id)
	qset = Profile.objects.filter(user__isnull=False).exclude(id__in=ids)
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectform.is_valid():
			admins = selectform.cleaned_data['email']
			for a in admins:
				new_profile = Profile.objects.filter(id=a.id).first()
				new_role, created = Role.objects.get_or_create(name='admin')
				new_profile_event = Profile_Dataset.objects.create(profile=new_profile, dataset=dataset, role=new_role)
			return HttpResponseRedirect(reverse('dataset_edit_members', kwargs={'id':dataset_id}))
	context = {
		"dataset": dataset,
		"selectform": selectform,
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
			new_dataset = Dataset.objects.create(title=dataset_title, description=desc)
			return HttpResponseRedirect(reverse('data_creation', kwargs={'id':new_dataset.id}))
	context = {
		"datasetform": datasetform,
	}
	return render(request, "dataset/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
		if len(profile_dataset) > 0:
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile).first()
			if not profile_dataset.is_admin():
				return HttpResponseRedirect(reverse('home'))
		else:
			return HttpResponseRedirect(reverse('home'))
	profile_dataset = None
	if request.user and (not request.user.is_anonymous()):
		profile = Profile.objects.filter(user=request.user)
		profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile)
		if len(profile_dataset) > 0:
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile).first()
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
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
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
			"grids": grids,
		}
		return render(request, "dataset/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_schedule(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
		context = {
			"dataset": dataset,
			"grids": grids,
			"schedule": schedule,
		}
		return render(request, "dataset/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_relations(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		relations = Event_Relation.objects.filter(dataset_associated=dataset)
		associated = Event_Relation.objects.filter(dataset_relation=dataset)
		context = {
			"dataset": dataset,
			"relations": relations,
			"grids": grids,
			"associated": associated
		}
		return render(request, "dataset/edit/relations.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_datas(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		context = {
			"dataset": dataset,
			"grids": grids,
			"datas": datas,
		}
		return render(request, "dataset/edit/datas.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_members(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		members = Profile_Dataset.objects.filter(dataset=dataset)
		context = {
			"dataset": dataset,
			"members": members,
			"grids": grids,
		}
		return render(request, "dataset/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_results(request, id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		news = News.objects.filter(dataset_id=id)
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		grid = Result_Grid.objects.filter(id=grid_id).first()
		headers = []
		scores = Score.objects.filter(result__grid=grid)
		header = Grid_Header.objects.filter(grid=grid)
		if scores.count() > 0:
			for h in header:
				if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
					headers.append(h)
		else:
			headers = header
		submission_scores = []
		submissions = Submission.objects.filter(grid=grid)
		for s in submissions:
			sub_scores = Score.objects.filter(submission=s)
			submission_scores.append((s,sub_scores))
		context = {
			"dataset": dataset,
			"grid": grid,
			"headers": headers,	
			"grids": grids,
			"submission_scores": submission_scores,
		}
		return render(request, "dataset/edit/results.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_news(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	news = News.objects.filter(dataset_id=id)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		context = {
			"news": news,
			"dataset": dataset,
			"grids": grids,
		}
		return render(request, "dataset/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_publications(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	news = News.objects.filter(dataset_id=id)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication_Dataset.objects.filter(dataset=dataset)
		context = {
			"news": news,
			"dataset": dataset,
			"publications": publications,
			"grids": grids,
		}
		return render(request, "dataset/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_col(request, id=None, col_id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		col = Col.objects.filter(id=col_id).first()
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
			"grids": grids,
		}
		return render(request, "dataset/edit/col.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_edit_submission(request, id=None, submission_id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	if check_edit_dataset_permission(request, dataset) == False:
		context = {
			"dataset": dataset,
			"news": news, 		
			"datas": datas,
			"grids": grids,
			"not_perm": True
		}
		return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))
	else:
		submission = Submission.objects.filter(id=submission_id).first()
		scores = Score.objects.filter(submission=submission)
		roweditform = ResultRowEditForm(scores=scores)
		subform = SubmissionEditForm(submission=submission)
		if request.method == 'POST':
			subform = SubmissionEditForm(request.POST, submission=submission)
			roweditform = ResultRowEditForm(request.POST, scores=scores)
			if subform.is_valid() and roweditform.is_valid():
				source_code = subform.cleaned_data['source_code']
				publication = subform.cleaned_data['publication']
				sub_file = subform.cleaned_data['sub_file']
				submission.source_code = source_code
				submission.publication = publication
				if sub_file:
					submission.sub_file = sub_file
				for s in scores:
					s.score = roweditform.cleaned_data[s.name]
					s.save()
				submission.save()
				return HttpResponseRedirect(reverse('dataset_edit_results', kwargs={'id':id, 'grid_id': submission.grid.id}))
		context = {
			"subform": subform,
			"roweditform": roweditform,
			"dataset": dataset,
			"grids": grids,
		}
		return render(request, "dataset/edit/submission.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def dataset_remove_submission(request, id=None, submission_id=None):
	submission = Submission.objects.filter(id=submission_id).first()
	submission.delete()
	return HttpResponse(reverse('dataset_edit_results', kwargs={'id':id, 'grid_id': submission.grid.id}))

@login_required(login_url='auth_login')
def dataset_publish(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	dataset.is_public = True
	dataset.save()
	return HttpResponseRedirect(reverse('dataset_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def dataset_unpublish(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	dataset.is_public = False
	dataset.save()
	return HttpResponseRedirect(reverse('dataset_edit_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def data_publish(request, dataset_id=None, id=None):
	data = Data.objects.filter(id=id).first()
	data.is_public = True
	data.save()
	return HttpResponseRedirect(reverse('data_desc', kwargs={'dataset_id':dataset_id,'id':id}))

@login_required(login_url='auth_login')
def data_unpublish(request, dataset_id=None, id=None):
	data = Data.objects.filter(id=id).first()
	data.is_public = False
	data.save()
	return HttpResponseRedirect(reverse('data_edit_desc', kwargs={'dataset_id':dataset_id,'id':id}))

def dataset_desc(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	publications = Publication_Dataset.objects.filter(dataset=dataset)
	context = {
		"grids": grids,
		"publications": publications,
		"dataset": dataset,
		"news": news, 		
		"datas": datas,
		"profile": profile_dataset,
	}
	return render(request, "dataset/desc.html", context, context_instance=RequestContext(request))

def dataset_schedule(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	publications = Publication_Dataset.objects.filter(dataset=dataset)
	context = {
		"grids": grids,
		"publications": publications,
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule,
		"profile": profile_dataset,
	}
	return render(request, "dataset/schedule.html", context, context_instance=RequestContext(request))

def dataset_associated_events(request, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	schedule = Schedule_Event.objects.filter(dataset_schedule=dataset).order_by('date')
	relations = Event_Relation.objects.filter(dataset_associated__id=dataset_id)
	associated = Event_Relation.objects.filter(dataset_relation=dataset)
	news = News.objects.filter(dataset_id=dataset_id)
	profile_dataset = check_dataset_permission(request, dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	publications = Publication_Dataset.objects.filter(dataset=dataset)
	context = {
		"grids": grids,
		"publications": publications,
		"dataset": dataset,
		"news": news, 
		"datas": datas,
		"schedule": schedule,
		"relations": relations,
		"associated": associated,
		"profile": profile_dataset,
	}
	return render(request, "dataset/relations.html", context, context_instance=RequestContext(request))

def dataset_publications(request, id=None):
	dataset = Dataset.objects.filter(id=id).first()
	datas = Data.objects.all().filter(dataset=dataset,is_public=True)
	news = News.objects.filter(dataset_id=id)
	profile_dataset = check_dataset_permission(request, dataset)
	publications = Publication_Dataset.objects.filter(dataset=dataset)
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	context = {
		"grids": grids,
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
	dataset = Dataset.objects.filter(id=id).first()
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
	# fileform = FileCreationForm()
	dataset = Dataset.objects.filter(id=id).first()
	if request.method == 'POST':
		dataform = DataCreationForm(request.POST)
		# fileform = FileCreationForm(request.POST, request.FILES)
		if dataform.is_valid():
			new_dataset = Dataset.objects.filter(id=id).first()
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
			return HttpResponseRedirect(reverse('data_edit_files', kwargs={'dataset_id':id,'id':new_data.id}))
	context = {
		"dataform": dataform,
		# "fileform": fileform,
		"dataset_id": id,
		"dataset": dataset,
	}
	return render(request, "data/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_remove(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id).first()
	data.delete()
	return HttpResponse(reverse('dataset_edit_datas', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def data_edit(request, id=None, dataset_id=None):
	data = Data.objects.filter(id=id).first()
	files = File.objects.filter(data=data)
	dataform = DataEditForm(data=data)
	dataset = Dataset.objects.filter(id=dataset_id).first()
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
	data = Data.objects.filter(id=id).first()
	dataform = DataEditForm(data=data)
	dataset = Dataset.objects.filter(id=dataset_id).first()
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
	data = Data.objects.filter(id=id).first()
	dataset = Dataset.objects.filter(id=dataset_id).first()
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
	data = Data.objects.filter(id=id).first()
	dataset = Dataset.objects.filter(id=dataset_id).first()
	fileform = FileCreationForm()
	if request.method == 'POST':
		fileform = FileCreationForm(request.POST, request.FILES)
		if fileform.is_valid():
			name = fileform.cleaned_data['name']
			url = fileform.cleaned_data['url']
			file = fileform.cleaned_data['file']
			if file:
				File.objects.create(name=name, file=file, data=data)
			if url:
				File.objects.create(name=name, url=url, data=data)
			return HttpResponseRedirect(reverse('data_edit_files', kwargs={'id':data.id, 'dataset_id': dataset_id}))
	context = {
		"data": data,
		"fileform": fileform,
		"dataset": dataset,
	}
	return render(request, "file/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def file_remove(request, id=None, file_id=None, dataset_id=None):
	new_file = File.objects.filter(id=file_id).first()
	new_file.delete()
	return HttpResponse(reverse('data_edit_files', kwargs={'id':id, 'dataset_id': dataset_id}))

def data_desc(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	data = Data.objects.filter(id=id).first()
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/desc.html", context, context_instance=RequestContext(request))

def data_software(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	data = Data.objects.filter(id=id).first()
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/software.html", context, context_instance=RequestContext(request))

def data_metric(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	data = Data.objects.filter(id=id).first()
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
	}
	return render(request, "data/metrics.html", context, context_instance=RequestContext(request))

def data_files(request, id=None, dataset_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	data = Data.objects.filter(id=id).first()
	files = File.objects.filter(data=data)
	news = News.objects.filter(dataset=dataset)
	context = {
		"data": data,
		"dataset": dataset,
		"news": news,
		"files": files,
	}
	return render(request, "data/files.html", context, context_instance=RequestContext(request))

def dataset_results(request, dataset_id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	grids = Result_Grid.objects.filter(track__dataset=dataset)
	news = News.objects.filter(dataset=dataset)
	datas = Data.objects.all().filter(dataset=dataset)	
	publications = Publication_Dataset.objects.filter(dataset=dataset)
	grid = Result_Grid.objects.filter(id=grid_id).first()
	results = None
	scores = None
	headers = []
	scores = Score.objects.filter(result__grid=grid)
	header = Grid_Header.objects.filter(grid=grid)
	results2 = Result.objects.filter(grid=grid)
	results = []
	for r in results2:
		extra = Result_User.objects.filter(result=r)
		results.append((r,extra))
	if scores.count() > 0:
		for h in header:
			if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
				headers.append(h)
	else:
		headers = header

	submission_scores = []
	submissions = Submission.objects.filter(grid=grid)
	for s in submissions:
		sub_scores = Score.objects.filter(submission=s)
		submission_scores.append((s,sub_scores))
	profile_dataset = check_dataset_permission(request, dataset)
	context = {
		"grids": grids,
		"grid": grid,
		"publications": publications,
		"dataset": dataset,
		"datas": datas,
		"news": news,
		"results": results,
		"scores": scores,
		"headers": headers,
		"submission_scores": submission_scores,
		"profile": profile_dataset,
	}
	return render(request, "dataset/results.html", context, context_instance=RequestContext(request))

def partner_list(request):
	partners = Partner.objects.all()
	global_partners = []
	event_partners = []
	for p in partners:
		if not Event_Partner.objects.filter(partner=p).exclude(event__isnull=True).count() > 0:
			global_partners.append((p))
	events = Event.objects.filter(is_public=True)
	for e in events:
		if Event_Partner.objects.filter(event=e).count() > 0:
			event_partners_aux = Event_Partner.objects.filter(event=e)
			partners_aux = []
			for ep in event_partners_aux:
				partners_aux.append((ep.partner))
			event_partners.append((ep.event, partners_aux))
	context = {
		"global_partners": global_partners,
		"event_partners": event_partners,
	}
	return render(request, "partner/list.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
@user_passes_test(lambda u:u.is_staff, login_url='/')
def partner_creation(request, id=None):
	partnerform = PartnerCreationForm()
	event = Event.objects.filter(id=id).first()
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
		"event": event,
	}
	return render(request, "partner/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def partner_select(request, id=None):
	event = Event.objects.filter(id=id).first()
	challenge = Challenge.objects.filter(id=id).first()
	workshop = Workshop.objects.filter(id=id).first()
	ids = []
	partners = Partner.objects.all()
	for p in partners:
		if Event_Partner.objects.filter(partner=p).exclude(event__isnull=True).count() == 0 or Event_Partner.objects.filter(partner=p, event__id=id).count() > 0:
			ids.append(p.id)
	qset = Partner.objects.exclude(id__in = ids)
	selectform = PartnerSelectForm(qset=qset)
	if request.method == 'POST':
		selectform = PartnerSelectForm(request.POST, qset=qset)
		if selectform.is_valid():
			partners = selectform.cleaned_data['partner']
			for p in partners:
				new_partner = Partner.objects.filter(id=p.id).first()
				new_event_partner = Event_Partner.objects.create(partner=new_partner, event=event)
			if Challenge.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('challenge_edit_sponsors', kwargs={'id':id}))
			elif Workshop.objects.filter(id=id).count() > 0:
				return HttpResponseRedirect(reverse('workshop_edit_sponsors', kwargs={'id':id}))
			else:
				return HttpResponseRedirect(reverse('home'))
	context = {
		"selectform": selectform,
		"event": event,
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
	event = Event.objects.filter(id=id).first()
	event.delete()
	if request.method == 'POST':
		return HttpResponse((reverse('event_list')))
		# return HttpResponse(reverse('event_list'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_relation_remove(request, id=None, relation_id=None, dataset_id=None):
	relation = Event_Relation.objects.filter(id=relation_id).first()
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
	profile = Profile_Event.objects.filter(id=member_id).first()
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
	profile = Profile_Dataset.objects.filter(id=member_id).first()
	profile.delete()
	return HttpResponse(reverse('dataset_edit_members', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_news_remove(request, id=None, news_id=None):
	news = News.objects.filter(id=news_id).first()
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
	news = News.objects.filter(id=news_id).first()
	news.delete()
	return HttpResponse(reverse('dataset_edit_news', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def dataset_schedule_remove(request, dataset_id=None, schedule_id=None):
	program = Schedule_Event.objects.filter(id=schedule_id).first()
	program.delete()
	return HttpResponse(reverse('dataset_edit_schedule', kwargs={'id':dataset_id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def workshop_program_remove(request, id=None, program_id=None):
	program = Schedule_Event.objects.filter(id=program_id).first()
	program.delete()
	if Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_program', kwargs={'id':id}))
	else:
		return HttpResponse(reverse('home'))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def event_schedule_remove(request, id=None, program_id=None):
	schedule = Schedule_Event.objects.filter(id=program_id).first()
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
def event_partner_remove(request, id=None, sponsor_id=None):
	partner = Event_Partner.objects.filter(id=sponsor_id).first()
	partner.delete()
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('challenge_edit_sponsors', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponse(reverse('workshop_edit_sponsors', kwargs={'id':id}))
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
			profile = Profile.objects.filter(user=request.user).first()
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
	proposal = Proposal.objects.filter(id=id).first()
	context = {
		"proposal": proposal,
	}
	return render(request, "proposal/detail.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def event_proposal_confirm(request, id=None):
	proposal = Proposal.objects.filter(id=id).first()
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
	challenge = Challenge.objects.filter(id=id).first()
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
		}
		return render(request, "challenge/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_schedule(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
			"challenge": challenge, 
			"schedule": schedule,
		}
		return render(request, "challenge/edit/schedule.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_relation(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
			"relations": relations,
			"associated": associated,
		}
		return render(request, "challenge/edit/relation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_result(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
			result = Result.objects.filter(challenge=challenge).first()
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
		}
		return render(request, "challenge/edit/result.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_members(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
		}
		return render(request, "challenge/edit/members.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_sponsors(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
		}
		return render(request, "challenge/edit/sponsors.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_sponsors_creation(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
				new_partner = Partner.objects.create(name=name, url=url, banner=banner, contact=new_contact)
				Event_Partner.objects.create(event=challenge, partner=new_partner)
				return HttpResponseRedirect(reverse('challenge_edit_sponsors', kwargs={'id':id}))
		context = {
			"partnerform": partnerform,
		}
		return render(request, "partner/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_tracks(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
	challenge = Challenge.objects.filter(id=id).first()
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
			"news": news
		}
		return render(request, "challenge/edit/news.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_edit_publications(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
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
		publications = Publication_Event.objects.filter(event=challenge)
		context = {
			"challenge": challenge, 
			"publications": publications,
		}
		return render(request, "challenge/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_edit(request, id=None, track_id=None, result_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	track = Track.objects.filter(id=track_id).first()
	result = Result.objects.filter(id=result_id).first()
	result_user = Result_User.objects.filter(result=result)
	scores = Score.objects.filter(result=result)
	if result_user:
		resulteditform = ResultUserEditForm(result_user=result_user)
		resultcreationform = ResultUserCreationForm()
		roweditform = ResultRowEditForm(scores=scores)
		if request.method == 'POST':
			if 'creation' in request.POST:
				resultcreationform = ResultUserCreationForm(request.POST)
				if resultcreationform.is_valid():
					name = resultcreationform.cleaned_data['name']
					link = resultcreationform.cleaned_data['link']
					Result_User.objects.create(name=name, link=link, result=result)
					return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
			elif 'edit' in request.POST:
				resulteditform = ResultUserEditForm(request.POST, result_user=result_user)
				roweditform = ResultRowEditForm(request.POST, scores=scores)
				if resulteditform.is_valid() and roweditform.is_valid():
					for s in scores:
						s.score = roweditform.cleaned_data[s.name]
						s.save()
					for r in result_user:
						r.link = resulteditform.cleaned_data[r.name]
						r.save()
					return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
		context = {
			"resulteditform": resulteditform,
			"resultcreationform": resultcreationform,
			"result_user": result_user,
			"roweditform": roweditform,
			"result": result,
		}
	else:
		resultcreationform = ResultUserCreationForm()
		roweditform = ResultRowEditForm(scores=scores)
		if request.method == 'POST':
			if 'creation' in request.POST:
				resultcreationform = ResultUserCreationForm(request.POST)
				if resultcreationform.is_valid():
					name = resultcreationform.cleaned_data['name']
					link = resultcreationform.cleaned_data['link']
					Result_User.objects.create(name=name, link=link, result=result)
					return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
			elif 'edit' in request.POST:
				roweditform = ResultRowEditForm(request.POST, scores=scores)
				if roweditform.is_valid():
					for s in scores:
						s.score = roweditform.cleaned_data[s.name]
						s.save()
					return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
		context = {
			"resultcreationform": resultcreationform,
			"roweditform": roweditform,
			"result": result,
		}
	return render(request, "track/edit/result_user.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_remove(request, id=None, track_id=None, result_id=None):
	result = Result.objects.filter(id=result_id).first()
	result.delete()
	return HttpResponse(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))

@login_required(login_url='auth_login')
def header_edit(request, id=None, track_id=None, header_id=None):
	header = Grid_Header.objects.filter(id=header_id).first()
	challenge = Challenge.objects.filter(id=id).first()
	track = Track.objects.filter(id=track_id).first()
	form = HeaderEditForm(header=header)
	if request.method == 'POST':
		form = HeaderEditForm(request.POST, header=header)
		if form.is_valid():
			name = form.cleaned_data['name']
			header.name = name
			header.save()
			return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
	context = {
		"form": form,
		"track": track,
		"challenge": challenge,
	}
	return render(request, "track/edit/header.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_new_table(request, id=None, track_id=None):
	track = Track.objects.filter(id=track_id).first()
	challenge = Challenge.objects.filter(id=id).first()
	form = ResultNewTableForm()
	if request.method == 'POST':
		form = ResultNewTableForm(request.POST)
		if form.is_valid():
			cols = form.cleaned_data['cols']
			if Result_Grid.objects.filter(track=track).count > 0:
				Result_Grid.objects.filter(track=track).delete()
				grid = Result_Grid.objects.create(track=track)
				i = 1
				while i <= cols:
					Grid_Header.objects.create(grid=grid, name='col'+str(i))
					i+=1
			return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
	context = {
		"form": form,
		"track": track,
		"challenge": challenge,
	}
	return render(request, "track/edit/new_table.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def result_new_row(request, id=None, track_id=None):
	track = Track.objects.filter(id=track_id).first()
	challenge = Challenge.objects.filter(id=id).first()
	grid = Result_Grid.objects.filter(track=track).first()
	headers = []
	scores = Score.objects.filter(result__grid=grid)
	if scores:
		header = Grid_Header.objects.filter(grid=grid)
		if scores.count() > 0:
			for h in header:
				if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
					headers.append(h)
		else:
			headers = header
	else:
		headers = Grid_Header.objects.filter(grid=grid)
	form = ResultRowForm(headers=headers)
	if request.method == 'POST':
		form = ResultRowForm(request.POST, headers=headers)
		if form.is_valid():
			username = form.cleaned_data['username']
			result = Result.objects.create(user=username, grid=grid)
			for h in headers: 
				new_score = form.cleaned_data[h.name]
				Score.objects.create(score=new_score, name=h.name, result=result)
			return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id, 'track_id':track_id}))
	context = {
		"form": form,
		"track": track,
		"challenge": challenge,
	}
	return render(request, "track/edit/new_row.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def challenge_publish(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	challenge.is_public = True
	challenge.save()
	return HttpResponseRedirect(reverse('challenge_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def challenge_unpublish(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	challenge.is_public = False
	challenge.save()
	return HttpResponseRedirect(reverse('challenge_edit_desc', kwargs={'id':id}))

def challenge_desc(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	sponsors = Event_Partner.objects.filter(event_id=id)
	publications = Publication_Event.objects.filter(event=challenge)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"challenge": challenge,
		"roles": roles,
		"news": news,
		"tracks": tracks,
		"profile": profile_event,
		"sponsors": sponsors,
		"publications": publications,
	}
	return render(request, "challenge/desc.html", context, context_instance=RequestContext(request))

def challenge_associated_events(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated=challenge)
	associated = Event_Relation.objects.filter(challenge_relation=challenge)
	profile_event = check_event_permission(request, challenge)
	sponsors = Event_Partner.objects.filter(event_id=id)
	publications = Publication_Event.objects.filter(event=challenge)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"sponsors": sponsors,
		"publications": publications,
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
	event = None
	dataset = None
	if dataset_id==None:
		event = Event.objects.filter(id=id).first()
	else:
		dataset = Dataset.objects.filter(id=dataset_id).first()
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
				event_associated = Event.objects.filter(id=id).first()	
				if Challenge.objects.filter(id=event_id).count() > 0:
					relation = Challenge.objects.filter(id=event_id).first()
					Event_Relation.objects.create(event_associated=event_associated,challenge_relation=relation,description=desc)
				elif Workshop.objects.filter(id=event_id).count() > 0:
					relation = Workshop.objects.filter(id=event_id).first()
					Event_Relation.objects.create(event_associated=event_associated,workshop_relation=relation,description=desc)
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					relation = Special_Issue.objects.filter(id=event_id).first()
					Event_Relation.objects.create(event_associated=event_associated,issue_relation=relation,description=desc)
				elif Dataset.objects.filter(id=event_id).count() > 0:
					relation = Dataset.objects.filter(id=event_id).first()
					Event_Relation.objects.create(event_associated=event_associated,dataset_relation=relation,description=desc)
			else:
				dataset_associated = Dataset.objects.filter(id=dataset_id).first()
				if Challenge.objects.filter(id=event_id).count() > 0:
					relation = Challenge.objects.filter(id=event_id).first()
					Event_Relation.objects.create(dataset_associated=dataset_associated,challenge_relation=relation,description=desc)
				elif Workshop.objects.filter(id=event_id).count() > 0:
					relation = Workshop.objects.filter(id=event_id).first()
					Event_Relation.objects.create(dataset_associated=dataset_associated,workshop_relation=relation,description=desc)
				elif Special_Issue.objects.filter(id=event_id).count() > 0:
					relation = Special_Issue.objects.filter(id=event_id).first()
					Event_Relation.objects.create(dataset_associated=dataset_associated,issue_relation=relation,description=desc)
				elif Dataset.objects.filter(id=event_id).count() > 0:
					relation = Dataset.objects.filter(id=event_id).first()
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
		"event": event,
		"dataset": dataset,
	}
	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

# @login_required(login_url='auth_login')
# def event_relation_edit(request, id=None, relation_id=None):
# 	c,w,d,s = None
# 	if dataset_id==None:
# 		c = Challenge.objects.filter(id=id).first()
# 		w = Workshop.objects.filter(id=id).first()
# 		s = Special_Issue.objects.filter(id=id).first()
# 	else:
# 		d = Dataset.objects.filter(id=dataset_id).first()
# 	relation = Event_Relation.objects.filter(id=relation_id).first()
# 	events = Event.objects.exclude(id__in = [id])
# 	datasets = Dataset.objects.exclude(id__in = [id])
# 	choices = []
# 	for x in events:
# 		choices.append((x.id, x.title)) 
# 	for d in datasets:
# 		choices.append((d.id, d.title)) 
# 	relationform = RelationEditForm(choices, relation=relation)
# 	if request.method == 'POST':
# 		relationform = RelationEditForm(choices, request.POST, relation=relation)
# 		if relationform.is_valid():
# 			event_associated = Event.objects.filter(id=id).first()
# 			desc = relationform.cleaned_data['description']
# 			event_id = relationform.cleaned_data['event']
# 			relation.description = desc  
# 			if Challenge.objects.filter(id=event_id).count() > 0:
# 				relation = Challenge.objects.filter(id=event_id).first()
# 				relation.challenge_relation=relation
# 			elif Workshop.objects.filter(id=event_id).count() > 0:
# 				relation = Workshop.objects.filter(id=event_id).first()
# 				relation.workshop_relation=relation
# 			elif Special_Issue.objects.filter(id=event_id).count() > 0:
# 				relation = Special_Issue.objects.filter(id=event_id).first()
# 				relation.issue_relation=relation
# 			elif Dataset.objects.filter(id=event_id).count() > 0:
# 				relation = Dataset.objects.filter(id=event_id).first()
# 				relation.dataset_relation=relation
# 			relation.save()
# 	context = {
# 		"relationform": relationform,
# 		"c": c, 
# 		"w": w, 
# 		"d": d, 
# 		"s": s,
# 	}
# 	return render(request, "relations/creation.html", context, context_instance=RequestContext(request))

def track_desc(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id).first()
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/desc.html", context, context_instance=RequestContext(request))

def track_metrics(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id).first()
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/metrics.html", context, context_instance=RequestContext(request))

def track_baseline(request, id=None,track_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id).first()
	context = {
		"challenge": challenge,
		"news": news,
		"track": track,
	}
	return render(request, "track/baseline.html", context, context_instance=RequestContext(request))

def track_result(request, id=None, track_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	track = Track.objects.filter(id=track_id).first()
	grid = Result_Grid.objects.filter(track=track)
	results = None
	scores = None
	headers = []
	if grid: 
		grid = Result_Grid.objects.filter(track=track).first()
		scores = Score.objects.filter(result__grid=grid)
		header = Grid_Header.objects.filter(grid=grid)
		results2 = Result.objects.filter(grid=grid)
		results = []
		for r in results2:
			extra = Result_User.objects.filter(result=r)
			results.append((r,extra))
		if scores.count() > 0:
			for h in header:
				if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
					headers.append(h)
		else:
			headers = header
	context = {
		"challenge": challenge,
		"track": track,
		"news": news,
		"results": results,
		"scores": scores,
		"headers": headers,	
	}
	return render(request, "track/result.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_creation(request, id=None):
	event = Challenge.objects.filter(id=id).first()
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
			dataset = Dataset.objects.filter(id=dataset_id).first()
			Track.objects.create(title=title, description=desc, metrics=metrics, baseline=baseline, dataset=dataset, challenge=event)
			return HttpResponseRedirect(reverse('challenge_edit_tracks', kwargs={'id':id}))
	context = {
		"trackform": trackform,
		"event": event,
	}
	return render(request, "track/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_edit_desc(request, id=None, track_id=None):
	c = Challenge.objects.filter(id=id).first()
	track = Track.objects.filter(id=track_id).first()
	if check_edit_event_permission(request, c) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "track/desc.html", context, context_instance=RequestContext(request))
	else:
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
				track.dataset = Dataset.objects.filter(id=dataset_id).first()
				track.save()
				return HttpResponseRedirect(reverse('track_desc', kwargs={'id':id, 'track_id': track_id}))
		context = {
			"trackform": trackform,
			"challenge": c,
			"track": track,
		}
		return render(request, "track/edit/desc.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_edit_result(request, id=None, track_id=None):
	c = Challenge.objects.filter(id=id).first()
	track = Track.objects.filter(id=track_id).first()
	if check_edit_event_permission(request, c) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"challenge": challenge, 
			"tracks": tracks,
			"news": news,
			"not_perm": True,
		}
		return render(request, "track/desc.html", context, context_instance=RequestContext(request))
	else:
		eventform = EditChallengeResult()
		grid = Result_Grid.objects.filter(track=track)
		results = None
		scores = None
		headers = []
		if grid: 
			grid = Result_Grid.objects.filter(track=track).first()
			scores = Score.objects.filter(result__grid=grid)
			header = Grid_Header.objects.filter(grid=grid)
			results = Result.objects.filter(grid=grid)
			if scores.count() > 0:
				for h in header:
					if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
						headers.append(h)
			else:
				headers = header
		if request.method == 'POST':
			eventform = EditChallengeResult(request.POST, request.FILES)
			if eventform.is_valid():
				if eventform.cleaned_data["file"]:
					Result_Grid.objects.filter(track=track).delete()
					grid = Result_Grid.objects.create(track=track)
					csv_file = csv.reader(eventform.cleaned_data["file"])
					titles = True
					names = None
					for line in csv_file:
						if len(line) > 1:
							if titles:
								print line
								for name in line:
									Grid_Header.objects.create(grid=grid, name=name)
								names = line
								titles = False
							else:
								result = Result.objects.create(grid=grid, user=line[0])
								i = 1
								for item in line:
									element = item.split()
									if len(element) > 0:
										element = element[0]
										try:
											digit = float(element)
											Score.objects.create(name=names[i], result=result, score=digit)
											i+=1
										except ValueError:
											continue
					return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id,'track_id':track_id}))
				else:
					return HttpResponseRedirect(reverse('result_new_table', kwargs={'id':id,'track_id':track_id}))
				return HttpResponseRedirect(reverse('track_edit_result', kwargs={'id':id,'track_id':track_id}))
		context = {
			"eventform": eventform,
			"challenge": c, 
			"track": track,
			"results": results,
			"scores": scores,
			"headers": headers,
		}
		return render(request, "track/edit/result.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def track_remove(request, id=None, track_id=None):
	track = Track.objects.filter(id=track_id).first()
	track.delete()
	return HttpResponse(reverse('challenge_edit_tracks', kwargs={'id':id}))

def challenge_members(request, id=None, role_id=None):
	challenge = Challenge.objects.filter(id=id).first()
	role = Role.objects.filter(id=role_id).first()
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	role = Role.objects.filter(id=role_id).first()
	members = Profile_Event.objects.filter(event=challenge,role=role)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	sponsors = Event_Partner.objects.filter(event_id=id)
	publications = Publication_Event.objects.filter(event=challenge)
	context = {
		"sponsors": sponsors,
		"publications": publications,
		"challenge": challenge,
		"members": members,
		"roles": roles,
		"news": news,
		"tracks": tracks,		
		"profile": profile_event,	
		"role": role,	
	}
	return render(request, "challenge/members.html", context, context_instance=RequestContext(request))

def challenge_sponsors(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	sponsors = Event_Partner.objects.filter(event_id=id)
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, challenge)
	publications = Publication_Event.objects.filter(event=challenge)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"challenge": challenge,
		"sponsors": sponsors,
		"news": news,
		"tracks": tracks,
		"profile": profile_event,		
	}
	return render(request, "challenge/sponsors.html", context, context_instance=RequestContext(request))

def challenge_schedule(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=challenge,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, challenge)
	sponsors = Event_Partner.objects.filter(event_id=id)
	publications = Publication_Event.objects.filter(event=challenge)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"sponsors": sponsors,
		"publications": publications,
		"challenge": challenge,
		"news": news,
		"schedule": schedule,
		"tracks": tracks,	
		"profile": profile_event,					
	}
	return render(request, "challenge/schedule.html", context, context_instance=RequestContext(request))

# def challenge_result(request, id=None):
# 	challenge = Challenge.objects.filter(id=id)[0]
# 	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
# 	news = News.objects.filter(event_id=id).order_by('-upload_date')
# 	result = Result.objects.filter(challenge=challenge)
# 	results = None
# 	scores = None
# 	names = None
# 	if result:
# 		result = Result.objects.filter(challenge=challenge)[0]
# 		scores = Score.objects.filter(result__challenge=challenge)
# 		results = Result.objects.filter(challenge=challenge)
# 		qset = Score.objects.filter(result=result)
# 		names = []
# 		for n in qset:
# 			names.append(n.name)
# 	profile_event = check_event_permission(request, challenge)
# 	sponsors = Event_Partner.objects.filter(event_id=id)
# 	publications = Publication_Event.objects.filter(event=challenge)
# 	context = {
# 		"sponsors": sponsors,
# 		"publications": publications,
# 		"challenge": challenge,
# 		"news": news,
# 		"tracks": tracks,
# 		"scores": scores,	
# 		"names": names,	
# 		"results": results,
# 		"profile": profile_event,		
# 	}
# 	return render(request, "challenge/result.html", context, context_instance=RequestContext(request))

def challenge_publications(request, id=None):
	challenge = Challenge.objects.filter(id=id).first()
	tracks = Track.objects.filter(challenge__id=id).exclude(dataset=None)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	publications = Publication_Event.objects.filter(event=challenge)
	profile_event = check_event_permission(request, challenge)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=challenge,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"sponsors": sponsors,
		"challenge": challenge,
		"news": news,
		"tracks": tracks,
		"publications": publications,
		"profile": profile_event,		
	}
	return render(request, "challenge/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=workshop, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=workshop, profile=profile).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
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
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	if check_edit_event_permission(request, workshop) == False:
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication_Event.objects.filter(event=workshop)
		context = {
			"workshop": workshop,
			"news": news,
			"publications": publications,
		}
		return render(request, "workshop/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_edit_sponsors(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	if check_edit_event_permission(request, workshop) == False:
		context = {
			"workshop": workshop,
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
		sponsors = Event_Partner.objects.filter(event_id=id)
		context = {
			"workshop": workshop, 
			"sponsors": sponsors,
		}
		return render(request, "workshop/edit/sponsors.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_sponsors_creation(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	if check_edit_event_permission(request, workshop) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"workshop": workshop, 
			"news": news,
			"not_perm": True,
		}
		return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))
	else:
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
				new_partner = Partner.objects.create(name=name, url=url, banner=banner, contact=new_contact)
				Event_Partner.objects.create(event=workshop, partner=new_partner)
				return HttpResponseRedirect(reverse('workshop_edit_sponsors', kwargs={'id':id}))
		context = {
			"partnerform": partnerform,
		}
		return render(request, "partner/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def workshop_publish(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	workshop.is_public = True
	workshop.save()
	return HttpResponseRedirect(reverse('workshop_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def workshop_unpublish(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	workshop.is_public = False
	workshop.save()
	return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':id}))

def workshop_desc(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"profile": profile_event,
		"sponsors": sponsors,				
	}
	return render(request, "workshop/desc.html", context, context_instance=RequestContext(request))

def workshop_schedule(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=workshop,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"schedule": schedule,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/schedule.html", context, context_instance=RequestContext(request))

def workshop_associated_events(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(workshop_relation=workshop)
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"relations": relations,
		"associated": associated,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/relation.html", context, context_instance=RequestContext(request))

def workshop_program(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	program = Schedule_Event.objects.filter(event_program=workshop,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"program": program,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/program.html", context, context_instance=RequestContext(request))

def workshop_members(request, id=None, role_id=None):
	workshop = Workshop.objects.filter(id=id).first()
	speakers = Profile_Event.objects.filter(role__name='speaker', event=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	role = Role.objects.filter(id=role_id).first()
	members = Profile_Event.objects.filter(event=workshop,role=role)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"members": members,
		"roles": roles,
		"role": role,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/members.html", context, context_instance=RequestContext(request))

def workshop_gallery(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	images = Gallery_Image.objects.filter(workshop=workshop)
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"workshop": workshop,
		"news": news,
		"images": images,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/gallery.html", context, context_instance=RequestContext(request))

def workshop_publications(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event_id=id)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"workshop": workshop,
		"news": news,
		"publications": publications,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/publications.html", context, context_instance=RequestContext(request))

def workshop_sponsors(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, workshop)
	publications = Publication_Event.objects.filter(event=workshop)
	sponsors = Event_Partner.objects.filter(event=workshop)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=workshop,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"workshop": workshop,
		"news": news,
		"publications": publications,
		"profile": profile_event,
		"sponsors": sponsors,
	}
	return render(request, "workshop/sponsors.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def add_gallery_picture(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	context = {
		"workshop": workshop, 
	}
	return render(request, "workshop/add_picture.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def remove_gallery_picture(request, id=None, pic_id=None):
	image = Gallery_Image.objects.filter(id=pic_id)
	image.delete()
	return HttpResponseRedirect(reverse('workshop_edit_gallery', kwargs={'id':id}))

@login_required(login_url='auth_login')
def remove_gallery(request, id=None):
	Gallery_Image.objects.filter(workshop__id=id).delete()
	return HttpResponseRedirect(reverse('workshop_edit_gallery', kwargs={'id':id}))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def edit_gallery_picture(request, id=None, pic_id=None):
	workshop = Workshop.objects.filter(id=id).first()
	image = Gallery_Image.objects.filter(id=pic_id).first()
	form = GalleryImageEditForm(image=image)
	if request.method == 'POST':
		form = GalleryImageEditForm(request.POST, image=image)
		if form.is_valid():
			desc = form.cleaned_data["desc"]
			image.description = desc
			image.save()
			return HttpResponseRedirect(reverse('workshop_edit_gallery', kwargs={'id':id}))
	context = {
		"workshop": workshop,
		"image": image,
		"form": form,
	}
	return render(request, "workshop/edit_picture.html", context, context_instance=RequestContext(request))

def speaker_select(request, id=None):
	choices = []
	workshop = Workshop.objects.filter(id=id).first()
	role1,created = Role.objects.get_or_create(name='Admin')
	role2,created = Role.objects.get_or_create(name='Speaker')
	ids = []
	ids.append(role1.id)
	ids.append(role2.id)
	roles = Role.objects.filter(id__in=ids)
	for r in roles:
	    choices.append((r.id, r.name))
	selectRoleForm = SelectRoleForm(choices)
	qset = Profile.objects.all()
	selectform = MemberSelectForm(qset=qset)
	if request.method == 'POST':
		selectRoleForm = SelectRoleForm(choices, request.POST)
		selectform = MemberSelectForm(request.POST, qset=qset)
		if selectRoleForm.is_valid() and selectform.is_valid():
			members = selectform.cleaned_data['email']
			role = Role.objects.filter(id=selectRoleForm.cleaned_data["role_select"]).first()
			for m in members:
				user = User.objects.filter(id=m.id).first()
				new_profile = Profile.objects.filter(user=user).first()
				new_profile_event = Profile_Event.objects.create(profile=new_profile, event=workshop, role=role)
			return HttpResponseRedirect(reverse('workshop_edit_members', kwargs={'id':id}))
	context = {
		"selectRoleForm": selectRoleForm,
		"selectform": selectform,
		"workshop": workshop,
	}
	return render(request, "speaker/select.html", context, context_instance=RequestContext(request))

def speaker_creation(request, id=None):
	workshop = Workshop.objects.filter(id=id).first()
	form = EditExtraForm()
	if request.method == 'POST':
		form = EditExtraForm(request.POST, request.FILES)
		if form.is_valid():
			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["last_name"]
			avatar = form.cleaned_data["avatar"]
			bio = form.cleaned_data["bio"]
			name = form.cleaned_data["name"]
			country = form.cleaned_data["country"]
			city = form.cleaned_data["city"]
			affiliation = Affiliation.objects.create(name=name, country=country, city=city)
			profile = Profile.objects.create(first_name=first_name, last_name=last_name, avatar=avatar, bio=bio, affiliation=affiliation)
			role = Role.objects.filter(name='Speaker').first()
			Profile_Event.objects.create(role=role, profile=profile, event=workshop)
			return HttpResponseRedirect(reverse('workshop_edit_members', kwargs={'id':id}))
	context = {
		"form": form,
		"workshop": workshop,
	}
	return render(request, "speaker/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_edit(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	if not request.user.is_staff:
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=issue, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=issue, profile=profile).first()
			if not profile_event.is_admin():
				return HttpResponseRedirect(reverse('home'))
		else:
			return HttpResponseRedirect(reverse('home'))
	profile_event = None
	if request.user and (not request.user.is_anonymous()):
		profile = Profile.objects.filter(user=request.user)
		profile_event = Profile_Event.objects.filter(event=issue, profile=profile)
		if len(profile_event) > 0:
			profile_event = Profile_Event.objects.filter(event=issue, profile=profile).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
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
	issue = Special_Issue.objects.filter(id=id).first()
	if check_edit_event_permission(request, issue) == False:
		news = News.objects.filter(event_id=id).order_by('-upload_date')
		context = {
			"issue": issue,
			"news": news,
			"not_perm": True,
		}
		return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))
	else:
		publications = Publication.objects.filter(issue=issue)
		context = {
			"issue": issue,
			"publications": publications,
		}
		return render(request, "special_issue/edit/publications.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def special_issue_publish(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	issue.is_public = True
	issue.save()
	return HttpResponseRedirect(reverse('special_issue_desc', kwargs={'id':id}))

@login_required(login_url='auth_login')
def special_issue_unpublish(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	issue.is_public = False
	issue.save()
	return HttpResponseRedirect(reverse('special_issue_edit_desc', kwargs={'id':id}))

def special_issue_desc(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(issue=issue)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			roles.append(r)
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	context = {
		"roles": roles,
		"publications": publications,
		"issue": issue,
		"news": news,
		"profile": profile_event,	
		"schedule": schedule,	
	}
	return render(request, "special_issue/desc.html", context, context_instance=RequestContext(request))

def special_issue_members(request, id=None, role_id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	role = Role.objects.filter(id=role_id).first()
	members = Profile_Event.objects.filter(event=issue,role=role).exclude(role__name='Admin')
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			roles.append(r)
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(issue=issue)
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	context = {
		"publications": publications,
		"issue": issue,
		"news": news,
		"members": members,
		"profile": profile_event,	
		"role": role,
		"roles": roles,
		"schedule": schedule,
	}
	return render(request, "special_issue/members.html", context, context_instance=RequestContext(request))

def special_issue_schedule(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(issue=issue)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			roles.append(r)
	context = {
		"roles": roles,
		"publications": publications,
		"issue": issue,
		"news": news,
		"schedule": schedule,
		"profile": profile_event,	
	}
	return render(request, "special_issue/schedule.html", context, context_instance=RequestContext(request))

def special_issue_associated_events(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	relations = Event_Relation.objects.filter(event_associated__id=id)
	associated = Event_Relation.objects.filter(issue_relation=issue)
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(issue=issue)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			roles.append(r)
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	context = {
		"roles": roles,
		"publications": publications,
		"issue": issue,
		"news": news,
		"relations": relations,
		"associated": associated,
		"profile": profile_event,	
		"schedule": schedule,
	}
	return render(request, "special_issue/relations.html", context, context_instance=RequestContext(request))

def special_issue_publications(request, id=None):
	issue = Special_Issue.objects.filter(id=id).first()
	news = News.objects.filter(event_id=id).order_by('-upload_date')
	profile_event = check_event_permission(request, issue)
	publications = Publication.objects.filter(issue=issue)
	roles_aux = Role.objects.all().exclude(name='Admin')
	roles = []
	for r in roles_aux:
		members2 = Profile_Event.objects.filter(event=issue,role=r)
		if members2.count() > 0:
			roles.append(r)
	schedule = Schedule_Event.objects.filter(event_schedule=issue,schedule_event_parent=None).order_by('date')
	context = {
		"roles": roles,
		"issue": issue,
		"news": news,
		"profile": profile_event,
		"publications": publications,
		"schedule": schedule,
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
	event = None
	dataset = None
	if dataset_id == None:
		event = Event.objects.filter(id=id).first()
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
		dataset = Dataset.objects.filter(id=dataset_id).first()
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
		"event": event,
		"dataset": dataset,
	}
	return render(request, "news/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def news_edit(request, id=None, dataset_id=None, news_id=None):
	news = News.objects.filter(id=news_id).first()
	event = Event.objects.filter(id=id).first()
	dataset = Dataset.objects.filter(id=dataset_id).first()
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
		"event": event,
		"dataset": dataset,
	}
	return render(request, "news/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_creation(request, dataset_id=None, id=None):
	scheduleform = ScheduleCreationForm()
	event = None
	dataset = None
	if dataset_id==None:
		event = Event.objects.filter(id=id).first()
	else:
		dataset = Dataset.objects.filter(id=dataset_id).first()
	if request.method == 'POST':
		scheduleform = ScheduleCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			if dataset_id==None:
				event = Event.objects.filter(id=id).first()
				new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,event_schedule=event)
				if Challenge.objects.filter(id=id).count() > 0:
					return HttpResponseRedirect(reverse('challenge_edit_schedule', kwargs={'id':id}))
				elif Workshop.objects.filter(id=id).count() > 0:
					return HttpResponseRedirect(reverse('workshop_edit_schedule', kwargs={'id':id}))
				elif Special_Issue.objects.filter(id=id).count() > 0:
					return HttpResponseRedirect(reverse('special_issue_edit_schedule', kwargs={'id':id}))
				else:
					return HttpResponseRedirect(reverse('home'))
			else:
				new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,dataset_schedule=dataset)
				if Dataset.objects.filter(id=dataset_id).count() > 0:
					return HttpResponseRedirect(reverse('dataset_edit_schedule', kwargs={'id':dataset_id}))
				else:
					return HttpResponseRedirect(reverse('home'))
	context = {
		"scheduleform": scheduleform,
		"event": event, 
		"dataset": dataset,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def program_creation(request, id=None):
	event = Event.objects.filter(id=id).first()
	scheduleform = ProgramCreationForm()
	if request.method == 'POST':
		scheduleform = ProgramCreationForm(request.POST)
		if scheduleform.is_valid():
			title = scheduleform.cleaned_data['title']
			desc = scheduleform.cleaned_data['description']
			time = scheduleform.cleaned_data['time']
			new_event = Schedule_Event.objects.create(title=title,description=desc,date=time,event_program=event)
			return HttpResponseRedirect(reverse('workshop_edit_program', kwargs={'id':id}))
	context = {
		"scheduleform": scheduleform,
		"event": event,
	}
	return render(request, "program/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def schedule_edit(request, id=None, dataset_id=None, schedule_id=None, program_id=None):
	if program_id==None:
		schedule = Schedule_Event.objects.filter(id=schedule_id).first()
		scheduleform = ScheduleEditForm(schedule=schedule)
		event = None
		dataset = None
		if dataset_id==None:
			event = Event.objects.filter(id=id).first()
		else:
			dataset = Dataset.objects.filter(id=dataset_id).first()
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
					if Challenge.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('challenge_edit_schedule', kwargs={'id':id}))
					elif Workshop.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('workshop_edit_schedule', kwargs={'id':id}))
					elif Special_Issue.objects.filter(id=id).count() > 0:
						return HttpResponseRedirect(reverse('special_issue_edit_schedule', kwargs={'id':id}))
					else:
						return HttpResponseRedirect(reverse('home'))
		context = {
			"scheduleform": scheduleform,
			"schedule": schedule,
			"event": event, 
			"dataset": dataset, 
		}
	else:
		schedule = Schedule_Event.objects.filter(id=program_id).first()
		# workshop = Workshop.objects.filter(id=event_id).first()
		event = None
		dataset = None
		if dataset_id==None:
			event = Event.objects.filter(id=id).first()
			print event
		else:
			dataset = Dataset.objects.filter(id=dataset_id).first()
			print dataset
		scheduleform = ProgramEditForm(schedule=schedule)		
		if request.method == 'POST':
			scheduleform = ProgramEditForm(request.POST, schedule=schedule)
			if scheduleform.is_valid():
				title = scheduleform.cleaned_data['title']
				desc = scheduleform.cleaned_data['description']
				time = scheduleform.cleaned_data['time']
				schedule.title = title
				schedule.description = desc
				schedule.date = time
				schedule.save()
				return HttpResponseRedirect(reverse('workshop_edit_program', kwargs={'id':id}))
		context = {
			"scheduleform": scheduleform,
			"schedule": schedule,
			"event": event,
			"dataset": dataset,
			# "workshop": workshop,
		}
	return render(request, "program/edit.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
# @user_passes_test(lambda u:u.is_staff, login_url='/')
def subevent_creation(request, event_id=None, program_id=None):
	event = Event.objects.filter(id=event_id).first()
	parent_event = Schedule_Event.objects.filter(id=program_id).first()
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
def submission_creation(request, dataset_id=None, grid_id=None):
	dataset = Dataset.objects.filter(id=dataset_id).first()
	grid = Result_Grid.objects.filter(id=grid_id).first()
	header = Grid_Header.objects.filter(grid=grid)
	scores = Score.objects.filter(result__grid=grid)
	headers = []
	if scores.count() > 0:
		for h in header:
			if Score.objects.filter(name=h.name, result__grid=grid).count() > 0:
				headers.append(h)
	else:
		headers = header
	form = SubmissionCreationForm()
	scoresform = SubmissionScoresForm(headers=headers)
	if request.method == 'POST':
		form = SubmissionCreationForm(request.POST, request.FILES)
		scoresform = SubmissionScoresForm(request.POST, headers=headers)
		if form.is_valid() and scoresform.is_valid():
			source_code = form.cleaned_data['source_code']
			publication = form.cleaned_data['publication']
			sub_file = form.cleaned_data['sub_file']
			if sub_file:
				new_submission = Submission.objects.create(source_code=source_code, publication=publication, sub_file=sub_file, user=request.user, grid=grid)
			else:
				new_submission = Submission.objects.create(source_code=source_code, publication=publication, user=request.user, grid=grid)
			for h in headers: 
				new_score = scoresform.cleaned_data[h.name]
				Score.objects.create(score=new_score, name=h.name, submission=new_submission)
			return HttpResponseRedirect(reverse('dataset_results', kwargs={'dataset_id':dataset_id, 'grid_id': grid_id}))
	context = {
		"form": form,
		"scoresform": scoresform,
	}
	return render(request, "dataset/submission.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def publication_creation(request, id=None):
	# If it creates by the global publications list
	if id==None:
		choices = []
		events = Event.objects.filter(is_public=True)
		datasets = Dataset.objects.filter(is_public=True)
		form = PublicationCreationForm(qset1=events, qset2=datasets)
		if request.method == 'POST':
			form = PublicationCreationForm(request.POST, qset1=events, qset2=datasets)
			if form.is_valid():
				title = form.cleaned_data['title']
				content = form.cleaned_data['content']
				if title:
					publi = Publication.objects.create(title=title, content=content)
				else:
					publi = Publication.objects.create(content=content)
				event = form.cleaned_data['event']
				dataset = form.cleaned_data['dataset']
				if event:
					for e in event:
						Publication_Event.objects.create(publication=publi, event=e)
				if dataset:
					for d in dataset:
						Publication_Dataset.objects.create(publication=publi, dataset=d)
				return HttpResponseRedirect(reverse('publication_list'))
	# If it creates by challenge, workshop, special issue, dataset edit mode.
	else:
		event = Event.objects.filter(id=id).first()
		dataset = Dataset.objects.filter(id=id).first()
		form = PublicationEventCreationForm()
		if request.method == 'POST':
			form = PublicationEventCreationForm(request.POST)
			if form.is_valid():
				title = form.cleaned_data['title']
				content = form.cleaned_data['content']
				if Event.objects.filter(id=id):
					if Special_Issue.objects.filter(id=id):
						issue = Special_Issue.objects.filter(id=id).first()
						if title:
							publi = Publication.objects.create(title=title, content=content, issue=issue)
						else:
							publi = Publication.objects.create(content=content, issue=issue)
						return HttpResponseRedirect(reverse('special_issue_edit_publications', kwargs={'id':id}))
					else:
						e = Event.objects.filter(id=id).first()
						if title:
							publi = Publication.objects.create(title=title, content=content)
						else:
							publi = Publication.objects.create(content=content)
						Publication_Event.objects.create(publication=publi, event=e)
						if Challenge.objects.filter(id=id).count() > 0:
							return HttpResponseRedirect(reverse('challenge_edit_publications', kwargs={'id':id}))
						elif Workshop.objects.filter(id=id).count() > 0:
							return HttpResponseRedirect(reverse('workshop_edit_publications', kwargs={'id':id}))
						elif Special_Issue.objects.filter(id=id).count() > 0:
							return HttpResponseRedirect(reverse('special_issue_edit_publications', kwargs={'id':id}))
				elif Dataset.objects.filter(id=id):
					d = Dataset.objects.filter(id=id).first()
					if title:
						publi = Publication.objects.create(title=title, content=content)
					else:
						publi = Publication.objects.create(content=content)
					Publication_Dataset.objects.create(publication=publi, dataset=d)
					return HttpResponseRedirect(reverse('dataset_edit_publications', kwargs={'id':id}))
	context = {
		"form": form,
		"event": event, 
		"dataset": dataset,
	}
	return render(request, "publication/creation.html", context, context_instance=RequestContext(request))

@login_required(login_url='auth_login')
def publication_edit(request, id=None, pub_id=None):
	publication = Publication.objects.filter(id=pub_id).first()
	event = Event.objects.filter(id=id).first()
	dataset = Dataset.objects.filter(id=id).first()
	form = PublicationEditForm(publication)
	if request.method == 'POST':
		form = PublicationEditForm(publication, request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			content = form.cleaned_data['content']
			publication.title = title
			publication.content = content
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
				return HttpResponseRedirect(reverse('publication_list'))
	context = {
		"form": form,
		"event": event, 
		"dataset": dataset,
	}
	return render(request, "publication/edit.html", context, context_instance=RequestContext(request))

def publication_list(request):
	publications_list = Publication.objects.all().exclude(issue__isnull=False)
	if check_staff_user(request):
		publications = []
		for p in publications_list:
			p_events = Publication_Event.objects.filter(publication=p)
			p_datasets = Publication_Dataset.objects.filter(publication=p)
			publications.append((p,p_events,p_datasets))
		context = {
			"publications": publications,
			"perm": True,
		}
	else:
		publications = []
		for p in publications_list:
			p_events = Publication_Event.objects.filter(publication=p)
			p_datasets = Publication_Dataset.objects.filter(publication=p)
			publications.append((p,p_events,p_datasets))
		context = {
			"publications": publications,
		}
	return render(request, "publication/list.html", context, context_instance=RequestContext(request))

def publication_detail(request, id=None):
	publication = Publication.objects.filter(id=id).first()
	publi_events = Publication_Event.objects.filter(publication=publication)
	publi_datasets = Publication_Dataset.objects.filter(publication=publication)
	context = {
		"publication": publication,
		"publi_datasets": publi_datasets,
		"publi_events": publi_events,
	}
	return render(request, "publication/detail.html", context, context_instance=RequestContext(request))

def publication_remove(request, id=None, pub_id=None):
	publication = Publication.objects.filter(id=pub_id).first()
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

def event_edit(request, id=None):
	if Challenge.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('challenge_edit_desc', kwargs={'id':id}))
	elif Workshop.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('workshop_edit_desc', kwargs={'id':id}))
	elif Special_Issue.objects.filter(id=id).count() > 0:
		return HttpResponseRedirect(reverse('special_issue_edit_desc', kwargs={'id':id}))

def check_event_permission(request, event):
	profile_event = None
	if request.user and (not request.user.is_anonymous()):
		if request.user.is_superuser or request.user.is_staff:
			profile_event = Profile.objects.filter(user=request.user)
		else:
			profile = Profile.objects.filter(user=request.user)
			profile_event = Profile_Event.objects.filter(event=event, profile=profile)
			if len(profile_event) > 0:
				profile_event = Profile_Event.objects.filter(event=event, profile=profile).first()
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
			profile_event = Profile_Event.objects.filter(event=event, profile=profile).first()
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
				profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile).first()
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
			profile_dataset = Profile_Dataset.objects.filter(dataset=dataset, profile=profile).first()
			if not profile_dataset.is_admin():
				return False
		else:
			return False

def check_staff_user(request):
	if request.user.is_staff or request.user.is_superuser:
		return True
	else:
		return False