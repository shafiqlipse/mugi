import django_filters
from .models import SchoolEnrollment


class SchoolEnrollmentFilter(django_filters.FilterSet):

    class Meta:
        model = SchoolEnrollment
        fields = [
            "school",
            "championship",
            "sport",
            "level",
        ]  # Add all fields you want to filter on
