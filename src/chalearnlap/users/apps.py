from __future__ import unicode_literals

from django.apps import AppConfig
from watson import search as watson


class UsersConfig(AppConfig):
    name = 'users'

    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        watson.register(self.get_model("Challenge").objects.filter(is_public=True))
        watson.register(self.get_model("Special_Issue").objects.filter(is_public=True))
        watson.register(self.get_model("Workshop").objects.filter(is_public=True))
        watson.register(self.get_model("Dataset").objects.filter(is_public=True))
