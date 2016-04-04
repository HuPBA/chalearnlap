from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Affiliation(models.Model):
	name = models.CharField(max_length=100)
	country = models.CharField(max_length=50)
	city = models.CharField(max_length=50)

	def __str__(self):
		return unicode(self.name).encode('utf-8')

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	affiliation = models.OneToOneField(Affiliation, on_delete=models.CASCADE, null=True)
	bio = models.TextField(max_length=300)
	image_path = models.CharField(max_length=200)

	def __str__(self):
		return unicode(self.user.username).encode('utf-8')