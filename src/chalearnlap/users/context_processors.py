from datetime import datetime
from django.conf import settings  
from .models import Track, CIMLBook, Challenge, Special_Issue, Workshop, Dataset, Profile, Profile_Event, Profile_Dataset


def base_context(request):
    challenges = Challenge.objects.filter(is_public=True).order_by('-id')
    special_issues = Special_Issue.objects.filter(is_public=True).order_by('-id')
    workshops = Workshop.objects.filter(is_public=True).order_by('-id')

    cimlbooks = CIMLBook.objects.all()
    tracks = Track.objects.all().order_by('-challenge__title')
    datasets = []
    for t in tracks:
        if t.dataset and t.dataset not in datasets:
            datasets.append(t.dataset)
    datasets = Dataset.objects.filter(is_public=True).order_by('-id')

    return dict(
        challenges = challenges,
        special_issues = special_issues,               
        workshops = workshops,
        datasets = datasets,
        cimlbooks = cimlbooks,
        chalearnlap_version = settings.CHALEARNLAP_VERSION,
    )
