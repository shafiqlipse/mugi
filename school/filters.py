import django_filters
from .models import *
from django.db.models import Q


class AthleteFilter(django_filters.FilterSet):

    gender = django_filters.ChoiceFilter(
        choices=[("Male", "Male"), ("Female", "Female")], label="Gender"
    )
    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.all(), label="School"
    )
    search = django_filters.CharFilter(method="filter_by_name", label="Name")

    index_number = django_filters.CharFilter(field_name="index_number", lookup_expr="icontains", label="Index Number")

    class Meta:
        model = Athlete
        fields = ["gender", "school", "search" ,"index_number"]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(Q(fname__icontains=value) | Q(mname__icontains=value))
