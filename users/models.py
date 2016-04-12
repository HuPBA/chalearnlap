from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Affiliation(models.Model):
	name = models.CharField(max_length=100)
	country = models.CharField(max_length=50)
	city = models.CharField(max_length=50)

	def __str__(self):
		return unicode(self.name).encode('utf-8')

class Event(models.Model):
	title = models.CharField(max_length=100)
	description = models.TextField(max_length=300)

	def __str__(self):
		return unicode(self.title).encode('utf-8')

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	first_name = models.CharField(max_length=30, null=True)
	last_name = models.CharField(max_length=30, null=True)
	affiliation = models.OneToOneField(Affiliation, on_delete=models.CASCADE, null=True)
	bio = models.TextField(max_length=300)
	image_path = models.CharField(max_length=200)
	events = models.ManyToManyField(Event, through='Profile_Event')

	def __str__(self):
		return unicode(self.user.username).encode('utf-8')

	def get_absolute_url(self):
		return reverse("detail", kwargs={"id": self.id})

class Profile_Event(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile')
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
	role = models.CharField(max_length=50)