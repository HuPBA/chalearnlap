from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from registration.signals import user_registered
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

import os

def user_registered_callback(sender, user, request, **kwargs):
	aff_name = request.POST.get('name','')
	aff_city = request.POST.get('city','')
	aff_country = request.POST.get('country','')
	bio = request.POST.get('bio','')
	first_name = request.POST.get('first_name','')
	last_name = request.POST.get('last_name','')
	avatar = request.FILES.get('avatar',None)
	if first_name == 'zyx':
		first_name = user.username
		last_name = ''
	new_affiliation = Affiliation.objects.create(name=aff_name, country=aff_country, city=aff_city)
	profile = Profile.objects.create(user=user, affiliation=new_affiliation, bio=bio, first_name=first_name, last_name=last_name, avatar=avatar)

user_registered.connect(user_registered_callback)

class Chalearn(models.Model):
	name = models.CharField(max_length=50)

class Affiliation(models.Model):
	name = models.CharField(max_length=100)
	country = models.CharField(max_length=50)
	city = models.CharField(max_length=50)

	def __str__(self):
		return unicode(self.name).encode('utf-8')

class Event(models.Model):
	title = models.CharField(max_length=100)
	description = RichTextField()
	parent_event = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
	chalearn = models.ForeignKey(Chalearn, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("event_edit", kwargs={"id": self.id})

def user_avatar_path(instance, filename):
	return 'userpics/%s-%s/%s' % (instance.first_name, instance.last_name, filename)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	first_name = models.CharField(max_length=30, null=True)
	last_name = models.CharField(max_length=30, null=True)
	affiliation = models.OneToOneField(Affiliation, on_delete=models.CASCADE, null=True)
	bio = models.TextField(max_length=3000)
	avatar = models.ImageField(upload_to=user_avatar_path, null=True, default='/static/images/default.jpg')
	events = models.ManyToManyField(Event, through='Profile_Event')

	def __str__(self):
		return unicode(self.first_name).encode('utf-8')

	def get_absolute_url(self):
		return reverse("profile_edit", kwargs={"id": self.id})

class Profile_Event(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='fk_profile')
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='fk_event')

class Role(models.Model):
	name = models.CharField(max_length=50)
	profile_event = models.ForeignKey(Profile_Event, on_delete=models.SET_NULL, null=True)

def partner_member_avatar_path(instance, filename):
	return 'partner/members/%s-%s/%s' % (instance.first_name, instance.last_name, filename)

class Contact(models.Model):
	first_name = models.CharField(max_length=30, null=True)
	last_name = models.CharField(max_length=30, null=True)
	bio = models.TextField(max_length=3000)
	avatar = models.ImageField(upload_to=partner_member_avatar_path, null=True, default='/static/images/default.jpg')
	email = models.CharField(max_length=100, null=True)

	def __str__(self):
		return unicode(self.first_name).encode('utf-8')

def partner_avatar_path(instance, filename):
	return 'partner/%s/%s' % (instance.name, filename)

class Partner(models.Model):
	name = models.CharField(max_length=100)
	url = models.CharField(max_length=500)
	banner = models.ImageField(upload_to=partner_avatar_path, null=True)
	events = models.ManyToManyField(Event, through='Event_Partner')
	contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return unicode(self.name).encode('utf-8')

class Event_Partner(models.Model):
	partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	role = models.CharField(max_length=50)

class Schedule_Event(models.Model):
	title = models.CharField(max_length=100, null=True)
	description = RichTextUploadingField()
	date = models.DateTimeField()
	parent_schedule_event = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class News(models.Model):
	title = models.CharField(max_length=100)
	description = RichTextField()
	upload_date = models.DateTimeField()
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.upload_date = timezone.now()
		return super(News, self).save(*args, **kwargs)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("news_edit", kwargs={"id": self.id})

class Special_Issue(Event):

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("special_issue_info", kwargs={"id": self.id})

class Workshop(Event):

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("workshop_info", kwargs={"id": self.id})

class Challenge(Event):

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("challenge_info", kwargs={"id": self.id})

class Dataset(models.Model):
	title = models.CharField(max_length=100, null=True)
	description = RichTextField()
	chalearn = models.ForeignKey(Chalearn, on_delete=models.SET_NULL, null=True)
	track = models.ManyToManyField(Challenge)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("dataset_edit", kwargs={"id": self.id})

class Result(models.Model):
	title = models.CharField(max_length=100)
	score = models.DecimalField(null=True, max_digits=15, decimal_places=10)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class Data(models.Model):
	title = models.CharField(max_length=100)
	description = RichTextField()
	dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

	def get_absolute_url(self):
		return reverse("data_detail", kwargs={"id": self.id, "dataset_id": self.dataset.id})

def data_path(instance, filename):
	return 'datasets/%s/%s/%s' % (instance.data.dataset.title, instance.data.title, filename)

class File(models.Model):
	name = models.CharField(max_length=100, null=True)
	file = models.FileField(upload_to=data_path, null=True)
	url = models.CharField(max_length=500, null=True)
	data = models.ForeignKey(Data, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.name).encode('utf-8')

	def filename(self):
		basename, extension = os.path.splitext(os.path.basename(self.file.name))
		return basename

class Publication(models.Model):
	publicated = models.BooleanField()
	result = models.ForeignKey(Result, on_delete=models.CASCADE)