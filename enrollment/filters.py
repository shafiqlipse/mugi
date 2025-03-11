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
    def __init__(self, *args, **kwargs):
        super(SchoolEnrollmentFilter, self).__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            field.widget.attrs.update({"class": "form-control"})