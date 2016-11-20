from datetime import datetime
from django.conf import settings  
from .models import Track, CIMLBook, Challenge, Special_Issue, Workshop, Dataset, Profile, Profile_Event, Profile_Dataset

def base_context(request):
    challenges = Challenge.objects.filter(is_public=True).order_by('title')
    special_issues = Special_Issue.objects.filter(is_public=True).order_by('title')
    workshops = Workshop.objects.filter(is_public=True).order_by('title')
    # datasets = Dataset.objects.filter(is_public=True).order_by('tracks__challenge__title')
    cimlbooks = CIMLBook.objects.all()
    tracks = Track.objects.all().order_by('-challenge__title')
    datasets = []
    for t in tracks:
        if t.dataset:
            if not t.dataset in datasets:
                datasets.append(t.dataset)
    # if request.user and (not request.user.is_anonymous()):
    #     profile = Profile.objects.filter(user=request.user)
    #     profile_event = Profile_Event.objects.filter(profile=profile)
    #     if len(profile_event) > 0:
    #         for p in profile_event:
    #             if p.is_admin() and p.event and p.profile:
    #                 if Challenge.objects.filter(id=p.event.id).count() > 0:
    #                     challenges = challenges | Challenge.objects.filter(id=p.event.id)
    #                 elif Workshop.objects.filter(id=p.event.id).count() > 0:
    #                     workshops = workshops | Workshop.objects.filter(id=p.event.id)
    #                 elif Special_Issue.objects.filter(id=p.event.id).count() > 0:
    #                     special_issues = special_issues | Special_Issue.objects.filter(id=p.event.id)
    #     profile_dataset = Profile_Dataset.objects.filter(profile=profile)
    #     if len(profile_dataset) > 0:
    #         for p in profile_dataset:
    #             if p.is_admin() and p.dataset and p.profile:
    #                 datasets = datasets | Dataset.objects.filter(id=p.dataset.id)
    return dict(
        challenges = challenges,
        special_issues = special_issues,               
        workshops = workshops,
        datasets = datasets,
        cimlbooks = cimlbooks,
    )