from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from registration.signals import user_registered

def user_registered_callback(sender, user, request, **kwargs):
	aff_name = request.POST["name"]
	aff_city = request.POST["city"]
	aff_country = request.POST["country"]
	bio = request.POST["bio"]
	first_name = request.POST["first_name"]
	last_name = request.POST["last_name"]
	avatar = request.POST["avatar"]
	new_affiliation = Affiliation(name=aff_name, country=aff_country, city=aff_city)
	new_affiliation.save()
	profile = Profile(user=user, affiliation=new_affiliation, bio=bio, first_name=first_name, last_name=last_name, avatar=avatar)
	profile.save()

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
	description = models.TextField()
	parent_event = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
	chalearn = models.ForeignKey(Chalearn, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	first_name = models.CharField(max_length=30, null=True)
	last_name = models.CharField(max_length=30, null=True)
	affiliation = models.OneToOneField(Affiliation, on_delete=models.CASCADE, null=True)
	bio = models.TextField(max_length=3000)
	avatar = models.ImageField(upload_to='userpics/', null=True)
	events = models.ManyToManyField(Event, through='Profile_Event')

	def __str__(self):
		return unicode(self.first_name).encode('utf-8')

	def get_absolute_url(self):
		return reverse("detail", kwargs={"id": self.id})

class Profile_Event(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='fk_profile')
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='fk_event')
	role = models.CharField(max_length=50)

class Partner(models.Model):
	name = models.CharField(max_length=100)
	url = models.CharField(max_length=200)
	banner = models.ImageField(upload_to='partnerpics/', null=True)
	events = models.ManyToManyField(Event, through='Challenge_Partner')

	def __str__(self):
		return unicode(self.name).encode('utf-8')

class Challenge_Partner(models.Model):
	partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	role = models.CharField(max_length=50)

class Schedule_Event(models.Model):
	description = models.TextField(max_length=3000)
	date = models.DateField(auto_now=True)
	parent_schedule_event = models.ForeignKey("self", on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.description).encode('utf-8')

class New(models.Model):
	description = models.TextField(max_length=3000)
	event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.description).encode('utf-8')

class Special_Issue(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	def __str__(self):
		return unicode(self.event.title).encode('utf-8')

class Workshop(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	def __str__(self):
		return unicode(self.event.title).encode('utf-8')

class Challenge(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	def __str__(self):
		return unicode(self.event.title).encode('utf-8')

class Dataset(models.Model):
	title = models.CharField(max_length=100, null=True)
	description = models.TextField(max_length=3000, null=True)
	chalearn = models.ForeignKey(Chalearn, on_delete=models.SET_NULL, null=True)

class Result(models.Model):
	title = models.CharField(max_length=100)
	score = models.DecimalField(null=True, max_digits=15, decimal_places=10)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class Data(models.Model):
	title = models.CharField(max_length=100)
	file = models.FileField(upload_to='data/', null=True)
	dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class Publication(models.Model):
	publicated = models.BooleanField()
	result = models.ForeignKey(Result, on_delete=models.CASCADE)