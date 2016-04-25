from django.contrib import admin
from .models import Profile, Affiliation, Event, Partner, Profile_Event, Schedule_Event, New, Workshop, Challenge, Special_Issue, Result, Data, Dataset, Chalearn, Publication, Member_Partner
# Register your models here.

admin.site.register(Profile)
admin.site.register(Affiliation)
admin.site.register(Event)
admin.site.register(Schedule_Event)
admin.site.register(Profile_Event)
admin.site.register(New)
admin.site.register(Workshop)
admin.site.register(Challenge)
admin.site.register(Special_Issue)
admin.site.register(Result)
admin.site.register(Data)
admin.site.register(Dataset)
admin.site.register(Chalearn)
admin.site.register(Publication)
admin.site.register(Member_Partner)
admin.site.register(Partner)