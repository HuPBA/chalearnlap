from __future__ import unicode_literals

from django.apps import AppConfig
from watson import search as watson


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        watson.register(self.get_model("Challenge"))
        watson.register(self.get_model("Special_Issue"))
        watson.register(self.get_model("Workshop"))
        watson.register(self.get_model("Dataset"))