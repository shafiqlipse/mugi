# analytics/services.py
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from accounts.models import *
from school.models import *
from enrollment.models import *
from transfers.models import *
# analytics/services.py
from datetime import timedelta
from django.utils import timezone

def month_comparison(qs, field="created"):
    now = timezone.localtime()
    this_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_start = (this_start - timedelta(days=1)).replace(day=1)

    this_month = qs.filter(**{f"{field}__gte": this_start}).count()
    prev_month = qs.filter(**{f"{field}__gte": prev_start, f"{field}__lt": this_start}).count()
    pct = round((this_month - prev_month) / prev_month * 100, 1) if prev_month else None
    return {"this": this_month, "prev": prev_month, "pct": pct}


def base_athletes():
    # One place that defines what counts as an athlete
    return Athlete.objects.exclude(status="COMPLETED")


def overview_counts():
    today = timezone.localdate()
    athletes = base_athletes().aggregate(
        total=Count("id"),
        male=Count("id", filter=Q(gender="male")),
        female=Count("id", filter=Q(gender="female")),
        today=Count("id", filter=Q(created=today)),   # was created__date
    )
    schools = School.objects.aggregate(
        total=Count("id"),
        today=Count("id", filter=Q(created=today)),   # was created__date
    )
    return {
        "athletes": athletes,
        "schools": schools,
        "officials": school_official.objects.count(),
    }


def participation_by_region():
    return (
        Region.objects
        .annotate(
            schools=Count("zone__district__school", distinct=True),
            athletes=Count("zone__district__school__athletes", distinct=True),
            male=Count("zone__district__school__athletes", distinct=True,
                       filter=Q(zone__district__school__athletes__gender="male")),
            female=Count("zone__district__school__athletes", distinct=True,
                         filter=Q(zone__district__school__athletes__gender="female")),
        )
        .values("name", "schools", "athletes", "male", "female")  # use your real field name
        .order_by("-athletes")
    )


def registrations_by_month():
    return list(
        base_athletes()
        .annotate(month=TruncMonth("created"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )


def athletes_by_status():
    return list(Athlete.objects.values("status").annotate(total=Count("id")).order_by("-total"))


def overview_cards():
    return {
        "schools":     {"total": School.objects.count(),
                        **month_comparison(School.objects.all())},
        "athletes":    {"total": base_athletes().count(),
                        **month_comparison(base_athletes())},
"officials":   {"total": school_official.objects.count(),
                **month_comparison(school_official.objects.all(), field="date_of_birth")},
"enrollments": {"total": SchoolEnrollment.objects.count(),
                **month_comparison(SchoolEnrollment.objects.all(), field="enrollment_date")},
"transfers":   {"total": TransferRequest.objects.count(),
                "approved": TransferRequest.objects.filter(status="APPROVED").count(),
                **month_comparison(TransferRequest.objects.all(), field="requested_at")},
    }