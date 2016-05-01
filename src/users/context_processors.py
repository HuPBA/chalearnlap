from datetime import datetime
from django.conf import settings  
from .models import Challenge, Special_Issue, Workshop, Dataset

def base_context(request):
    challenges = Challenge.objects.all()
    special_issues = Special_Issue.objects.all()
    workshops = Workshop.objects.all()
    datasets = Dataset.objects.all()

    return dict(
        challenges = challenges,
        special_issues = special_issues,               
        workshops = workshops,
        datasets = datasets,
    )