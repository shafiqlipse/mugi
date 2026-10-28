from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.decorators import *
from school.models import *
from accounts.models import *
from django.contrib import messages
from .forms import *
from .models import *
today = timezone.now().date()
from django.db.models import Count
from django.utils import timezone
from django.db.models import Q
from .services import *

# Filter schools created today
@login_required(login_url="login")
def dashboard(request):

    athletes = (
        Athlete.objects.select_related("school")
        .exclude(status="COMPLETED")
        .order_by("-created")[:5]
    )
    context = {
        "cards": overview_cards(),
        "athletes": athletes,
    }
    return render(request, "dashboard/overview.html", context)




@school_required
def school_dashboard(request):
    school = request.user.school

    # Fetch all athletes related to the school once
    athletes_qs = Athlete.objects.filter(school=school,status="ACTIVE").select_related("school")

    # Aggregate athlete counts in a single query
    athlete_counts = athletes_qs.aggregate(
        total=Count("id"),
        male=Count("id", filter=Q(gender="male")),
        female=Count("id", filter=Q(gender="female"))
    )

    # Aggregate officials counts in a single query
    officials_counts = school_official.objects.filter(school=school).aggregate(
        total=Count("id"),
        male=Count("id", filter=Q(gender="M")),
        female=Count("id", filter=Q(gender="F"))
    )

    context = {
        "athletes": athletes_qs.select_related("school")[:6],  # Fetch only 6 for display
        "athletes_count": athlete_counts["total"],
        "athletes_bcount": athlete_counts["male"],
        "athletes_gcount": athlete_counts["female"],
        "officials_count": officials_counts["total"],
        "officials_bcount": officials_counts["male"],
        "officials_gcount": officials_counts["female"],
    }

    return render(request, "dashboard/school_dashboard.html", context)

