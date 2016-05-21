from django.contrib import admin
from .models import Profile, Affiliation, Event, File, Partner, Event_Partner, Profile_Event, Schedule_Event, News, Workshop, Challenge, Special_Issue, Result, Data, Dataset, Chalearn, Publication, Contact
# Register your models here.

admin.site.register(Profile)
admin.site.register(Affiliation)
admin.site.register(Event)
admin.site.register(Schedule_Event)
admin.site.register(Profile_Event)
admin.site.register(News)
admin.site.register(Workshop)
admin.site.register(Challenge)
admin.site.register(Special_Issue)
admin.site.register(Event_Partner)
admin.site.register(Result)
admin.site.register(Data)
admin.site.register(Dataset)
admin.site.register(Chalearn)
admin.site.register(Publication)
admin.site.register(Contact)
admin.site.register(Partner)
admin.site.register(File)