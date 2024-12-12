import django_filters
from .models import *


class TraineeFilter(django_filters.FilterSet):

    gender = django_filters.ChoiceFilter(
        choices=[("Male", "Male"), ("Female", "Female")], label="Gender"
    )
    level = django_filters.ChoiceFilter(
        choices=[("Level 1", "Level 1"), ("Level 2", "Level 2")], label="Level"
    )
    venue = django_filters.ModelChoiceFilter(
        queryset=Venue.objects.all(), label="Venue"
    )
    discipline = django_filters.ModelChoiceFilter(
        queryset=Discipline.objects.all(), label="Discipline"
    )
    course = django_filters.ChoiceFilter(
        choices=[
            ("Refereeing", "Refereeing"),
            ("Coaching", "Coaching"),
            ("Media", "Media"),
            ("Safeguarding", "Safeguarding"),
            ("First-Aid", "First-Aid"),
            ("Umpiring", "Umpiring"),
            ("Officiating", "Officiating"),
            (
                "SPORTS FACILITIES FACILITY MANAGEMENT",
                "SPORTS FACILITIES FACILITY MANAGEMENT",
            ),
        ],
        label="Course",
    )

    class Meta:
        model = Trainee
        fields = ["gender", "venue", "discipline", "course", "level"]
