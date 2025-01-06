from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.decorators import admin_required
from school.models import *
from accounts.models import *
from transfers.models import *
from django.contrib import messages
from .forms import *
from .models import *
today = timezone.now().date()
from django.db.models import Count
from django.utils import timezone
from django.db.models import Q

# Filter schools created today
@login_required
def dashboard(request):
    users_count = User.objects.filter(is_staff=True).count
    schools_count = School.objects.all().count
    regions = Region.objects.annotate(
        school_count=Count("zone__district__school"),
        athlete_count=Count("zone__district__school__athletes"),
    )
    officials_count = school_official.objects.all().count
    schools_today = School.objects.filter(created=today).count
    athletes_today = Athlete.objects.filter(created=today).count
    athletes_count = Athlete.objects.all().count
    schools = School.objects.all().order_by("-created")[:5]
    athletes = Athlete.objects.all().order_by("-created")[:6]
    context = {
        "users_count": users_count,
        "schools_count": schools_count,
        "officials_count": officials_count,
        "schools": schools,
        "athletes": athletes,
        "regions": regions,
        "athletes_count": athletes_count,
        "schools_today": schools_today,
        "athletes_today": athletes_today,
    }
    return render(request, "dashboard/overview.html", context)


# championships
# @admin_required
def championships(request):
    championships = Championship.objects.all()
    new_championship = None

    if request.method == "POST":
        sform = ChampionshipForm(request.POST, request.FILES)

        if sform.is_valid():
            new_championship = sform.save(commit=False)

            new_championship.save()
            return redirect("championships")
    else:
        sform = ChampionshipForm()
    context = {"championships": championships, "sform": sform}
    return render(request, "all/championships.html", context)


@admin_required
def championship_details(request, id):
    championship = get_object_or_404(Championship, id=id)

    context = {"championship": championship}
    return render(request, "all/championship.html", context)


@admin_required
def championship_update(request, id):
    championship = get_object_or_404(Championship, id=id)

    if request.method == "POST":
        form = ChampionshipForm(request.POST, request.FILES, instance=championship)
        if form.is_valid():
            form.save()
            messages.success(request, "Championship information updated successfully!")
            return redirect("championship", id=championship.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChampionshipForm(instance=championship)

    context = {
        "form": form,
        "championship": championship,
    }
    return render(request, "all/update_championship.html", context)


@admin_required
def championship_delete(request, id):
    stud = Championship.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("championships")

    return render(request, "all/delete_championship.html", {"obj": stud})


# sports


def sports(request):
    sports = Sport.objects.all()
    new_sport = None

    if request.method == "POST":
        sform = SportForm(request.POST, request.FILES)

        if sform.is_valid():
            new_sport = sform.save(commit=False)

            new_sport.save()
            return redirect("sports")
    else:
        sform = SportForm()
    context = {"sports": sports, "sform": sform}
    return render(request, "sport/sports.html", context)


@admin_required
def sport_details(request, id):
    sport = Sport.objects.get(id=id)

    context = {"sport": sport}
    return render(request, "sport/sport.html", context)


@admin_required
def sport_update(request, id):
    sport = get_object_or_404(Sport, id=id)

    if request.method == "POST":
        form = SportForm(request.POST, request.FILES, instance=sport)
        if form.is_valid():
            form.save()
            messages.success(request, "Sport information updated successfully!")
            return redirect("sport", id=sport.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SportForm(instance=sport)

    context = {
        "form": form,
        "sport": sport,
    }
    return render(request, "sport/update_sport.html", context)


@admin_required
def sport_delete(request, id):
    stud = Sport.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("sports")

    return render(request, "sport/delete_sport.html", {"obj": stud})


# @transfer_required
def AllTransfers(request):
    transfers = TransferRequest.objects.filter(status ='Accepted')
    context = {"transfers": transfers}
    return render(request, "all/transfers.html", context)

# @transfer_required
def All_Transfers(request):
    transfers = TransferRequest.objects.all()
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)

def announcement_add(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'your_template.html', {'announcements': announcements})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Announcement
from .forms import AnnouncementForm
import base64
from django.utils.timezone import now

def announcement(request):
   
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                announce = form.save(commit=False)

                # Handle cropped image data for the "banner" field
                cropped_data = request.POST.get("banner_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f"banner.{ext}")
                        announce.banner = data
                    except (ValueError, TypeError) as e:
                        messages.error(request, "Invalid image data.")
                        return render(request, "all/announce.html", {"form": form})

                announce.save()
                messages.success(request, "Announcement added successfully!")
                return redirect("announcement")

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                return render(request, "all/anounce.html", {"form": form})

        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = AnnouncementForm()

    context = {"form": form}
    return render(request, "all/anounce.html", context)


def announcements(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, "all/announcements.html", {"announcements": announcements})