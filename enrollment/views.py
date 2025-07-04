from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from xhtml2pdf import pisa
from io import BytesIO
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.core.paginator import Paginator

from .filters import SchoolEnrollmentFilter  # Assume you have created this filter
from django.http import JsonResponse


def get_sports(request):
    championship_id = request.GET.get("championship_id")
    if championship_id:
        try:
            championship = Championship.objects.get(id=championship_id)
            sports = championship.sport.values("id", "name")  # Correct accessor
            return JsonResponse(list(sports), safe=False)
        except Championship.DoesNotExist:
            return JsonResponse({"error": "Championship not found"}, status=404)
    return JsonResponse([], safe=False)

from django.db import IntegrityError
from django.contrib import messages
@login_required(login_url="login")
def SchoolEnrollments(request):
    school = request.user.school
    enrollments = SchoolEnrollment.objects.select_related("school").filter(school=school)

    if request.method == "POST":
        form = SchoolEnrollmentForm(request.POST, request.FILES)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.school = school
            try:
                enrollment.save()
                messages.success(request, "Enrollment created successfully!")
                return redirect("school_enrollments")
            except IntegrityError:
                messages.error(
                    request,
                    "This school is already enrolled in the same championship, sport, and level."
                )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolEnrollmentForm()

    context = {"form": form, "enrollments": enrollments}
    return render(request, "enrollments/school_enrolls.html", context)


@login_required(login_url="login")
def athleticsEnrollments(request):
    enrollment0s = AthleticsEnrollment.objects.all()

    if request.method == "POST":
        form = AthleticsEnrollmentForm(request.POST, request.FILES)

        if form.is_valid():
            enrollment = form.save(commit=False)
     
            try:
                enrollment.save()
                messages.success(request, "Enrollment created successfully!")
                return redirect("athletics_enrollments")
            except IntegrityError:
                messages.error(
                    request,
                    "This school is already enrolled in the same championship, sport, and level."
                )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AthleticsEnrollmentForm()

    context = {"form": form, "enrollment0s": enrollment0s}
    return render(request, "athletics/athletics.html", context)


@login_required(login_url="login")
def AchivesEnrollments(request):
    # Get all school_enrolls
    school_enrolls = SchoolEnrollment.objects.select_related("school").filter(championship__status='Inactive').order_by("id")


     # Apply filtering
    school_enroll_filter = SchoolEnrollmentFilter(request.GET, queryset=school_enrolls)
    filtered_enrolls = school_enroll_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_enrolls, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_enrolls = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "enrolls": paginated_enrolls,
        "school_enroll_filter": school_enroll_filter,
    }

    # Prepare context with athletes data


    return render(request, "enrollments/enroll.html", context)

@login_required(login_url="login")
def ActiveEnrollments(request):
    # Get all school_enrolls
    school_enrolls = SchoolEnrollment.objects.select_related("school").filter(championship__status='Active').order_by("id")


     # Apply filtering
    school_enroll_filter = SchoolEnrollmentFilter(request.GET, queryset=school_enrolls)
    filtered_enrolls = school_enroll_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_enrolls, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_enrolls = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "enrolls": paginated_enrolls,
        "school_enroll_filter": school_enroll_filter,
    }

    # Prepare context with athletes data


    return render(request, "enrollments/enroll.html", context)

@login_required(login_url="login")
def remove_athlete(request, enrollment_id, athlete_id):
    athlete_enrollment = get_object_or_404(AthleteEnrollment, id=enrollment_id)
    athlete = get_object_or_404(Athlete, id=athlete_id)

    if request.method == "POST":
        athlete_enrollment.athletes.remove(athlete)
        return HttpResponseRedirect(
            reverse("school_enrollment", args=[athlete_enrollment.school_enrollment.id])
        )

    return redirect(
        "enrollments/school_enrollment", id=athlete_enrollment.school_enrollment.id
    )

@login_required(login_url="login")
def school_enrollment_details(request, id):
    school_enrollment = get_object_or_404(SchoolEnrollment, id=id)
    school = school_enrollment.school
    if request.method == "POST":
        form = AthleteEnrollmentForm(request.POST)
        if form.is_valid():
            selected_athletes = form.cleaned_data["athletes"]
            already_enrolled = AthleteEnrollment.objects.filter(
                school_enrollment=school_enrollment,
                athletes__in=selected_athletes
            ).values_list("athletes__id", flat=True).distinct()

            if already_enrolled:
                messages.error(request, "Some of the selected athletes are already enrolled in this school enrollment.")
            else:
                current_total = Athlete.objects.filter(
                    athleteenrollment__school_enrollment=school_enrollment
                ).distinct().count()


                if current_total + selected_athletes.count() > school_enrollment.sport.entries:
                    messages.error(
                        request,
                        f"You can only enroll {school_enrollment.sport.entries - current_total} more athlete(s) for this sport."
                    )
                else:
                    athlete_enrollment = AthleteEnrollment.objects.create(
                        school_enrollment=school_enrollment,
                        enrolled_by=request.user
                    )
                    athlete_enrollment.athletes.set(selected_athletes)
                    messages.success(request, "Athletes enrolled successfully.")
                    return HttpResponseRedirect(reverse("school_enrollment", args=[id]))
    else:
        form = AthleteEnrollmentForm()

    athlete_enrollments = AthleteEnrollment.objects.filter(
        school_enrollment=school_enrollment
    )
    all_athletes = Athlete.objects.filter(school=school, status="ACTIVE")

    context = {
        "school_enrollment": school_enrollment,
        "form": form,
        "athlete_enrollments": athlete_enrollments,
        "all_athletes": all_athletes,
    }
    return render(request, "enrollments/school_enroll.html", context)


# @login_required(login_url="login")
# @login_required(login_url="login")
# @login_required(login_url="login")
@login_required(login_url="login")
def athletics_enrollment_details(request, id):
    athletics_enrollment = get_object_or_404(AthleticsEnrollment, id=id)
    zone = athletics_enrollment.zone
    if request.method == "POST":
        form = AthleticsAthletesForm(request.POST)
        if form.is_valid():
            selected_athletes = form.cleaned_data["athletes"]
            already_enrolled = AthleticsAthletes.objects.filter(
                school_enrollment=athletics_enrollment,
                athletes__in=selected_athletes
            ).values_list("athletes__id", flat=True).distinct()

            if already_enrolled:
                messages.error(request, "Some of the selected athletes are already enrolled in this athletics enrollment.")
            else:
                current_total = Athlete.objects.filter(
                    athleticsathletes__school_enrollment=athletics_enrollment
                ).distinct().count()

                allowed_entries = athletics_enrollment.sport.entries

                if current_total + selected_athletes.count() > allowed_entries:
                    remaining = allowed_entries - current_total
                    messages.error(
                        request,
                        f"You can only enroll {remaining} more athlete(s) for this sport."
                    )
                else:
                    athlete_enrollment = AthleticsAthletes.objects.create(
                        school_enrollment=athletics_enrollment,
                        enrolled_by=request.user
                    )

                    athlete_enrollment.athletes.set(selected_athletes)
                    messages.success(request, "Athletes enrolled successfully.")
                    return HttpResponseRedirect(reverse("athletics_enrollment", args=[id]))
    else:
        form = AthleticsAthletesForm()

    athlete_enrollments = AthleticsAthletes.objects.filter(
       school_enrollment_id=id
    )
    all_athletes = Athlete.objects.filter(school__district__zone=zone, status="ACTIVE")

    context = {
        "athletics_enrollment": athletics_enrollment,
        "form": form,
        "athlete_enrollments": athlete_enrollments,
        "all_athletes": all_athletes,
    }
    return render(request, "athletics/athletics_team.html", context)


@login_required(login_url="login")
def school_enrollment_update(request, id):
    school_enrollment = get_object_or_404(SchoolEnrollment, id=id)

    if request.method == "POST":
        form = SchoolEnrollmentForm(
            request.POST, request.FILES, instance=school_enrollment
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "SchoolEnrollment information updated successfully!"
            )
            return redirect("school_enrollment", id=school_enrollment.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolEnrollmentForm(instance=school_enrollment)

    context = {
        "form": form,
        "school_enrollment": school_enrollment,
    }
    return render(request, "enrollments/update_school_enroll.html", context)

@login_required(login_url="login")
def school_enroll_delete(request, id):
    stud = SchoolEnrollment.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("school_enrollments")

    return render(request, "enrollments/delete_school_enroll.html", {"obj": stud})


from django.shortcuts import render
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Make sure to import your models

admin_required

@login_required(login_url="login")
def Accreditation(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    athlete_enrollments = AthleteEnrollment.objects.select_related("school").filter(school_enrollment=team)
    athletes = Athlete.objects.filter(athleteenrollment__in=athlete_enrollments)

    # Get template
    template = get_template("reports/acred.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "athletes": athletes,
        "team": team,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Accreditation.pdf"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response

@login_required(login_url="login")
def Occreditation(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    
    officials = school_official.objects.filter(school=team.school).exclude(status="Inactive")

    # Get template
    if request.method == "POST":
        # Get list of official IDs to exclude
        excluded_ids = request.POST.getlist("exclude_officials")
        if excluded_ids:
            officials = officials.exclude(id__in=excluded_ids)
    # Get template
    template = get_template("reports/ocred.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "officials": officials,
        "team": team,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Occreditation.pdf"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response

from django.db.models import F, ExpressionWrapper, IntegerField, Case, When, Value
from datetime import date
@login_required(login_url="login")
def Albums(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    athlete_enrollments = AthleteEnrollment.objects.filter(school_enrollment=team)
    today = date.today()
    athletes = Athlete.objects.filter(athleteenrollment__in=athlete_enrollments).distinct().annotate(
        age=ExpressionWrapper(
            today.year - F('date_of_birth__year') - 
            Case(
                When(date_of_birth__month__gt=today.month, then=Value(1)),
                When(date_of_birth__month=today.month, date_of_birth__day__gt=today.day, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            ),
            output_field=IntegerField()
        )
    )
    school = team.school
    officials = school_official.objects.filter(school=school).exclude(status="Inactive")

    # Get athlete and official counts
    athlete_count = athletes.count()
    official_count = officials.count()

    # Create a unique filename
    filename = f"{team.school} | {team.sport} .pdf"

    # Get template
    template = get_template("reports/albums.html")

    # Prepare context
    context = {
        "team": team,
        "official_count": official_count,
        "athlete_count": athlete_count,
        "athletes": athletes,
        "officials": officials,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response


admin_required

@login_required(login_url="login")
def Certificate(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    athlete_enrollments = AthleteEnrollment.objects.filter(school_enrollment=team)
    athletes = Athlete.objects.filter(athleteenrollment__in=athlete_enrollments)

    # Get template
    template = get_template("reports/cert.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "team": team,
        "athletes": athletes,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Accreditation.pdf"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response

@login_required(login_url="login")
def Cortificate(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    
    officials = school_official.objects.filter(school=team.school).exclude(status="Inactive")
    
    if request.method == "POST":
        # Get list of official IDs to exclude
        excluded_ids = request.POST.getlist("exclude_officials")
        if excluded_ids:
            officials = officials.exclude(id__in=excluded_ids)
    # Get template
    template = get_template("reports/cort.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "officials": officials,
        "team": team,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Cortificate.pdf"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response



import csv
from django.http import HttpResponse

def export_ecsv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="enrollments.csv"'

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        "Enrollment ID",
        "School",
        "District",
        "Zone",
        "Championship",
        "Sport",
        "level",
        "first Name",
        "last Name",
        "Date of Birth",
        "Index Number",
    ])

    for enrollment in SchoolEnrollment.objects.select_related("school").filter(level='National', championship__status='Active'):
        for athlete_enrollment in enrollment.athlete_enrollments.all():
            for athlete in athlete_enrollment.athletes.all():
                writer.writerow([
                    enrollment.id,
                    enrollment.school.name,
                    enrollment.school.district.name if enrollment.school.district else "",
                    enrollment.school.district.zone.name if enrollment.school.district and enrollment.school.district.zone else "",
                    enrollment.championship.name,
                    enrollment.sport.name,
                    enrollment.level,
                    athlete.fname,
                    athlete.lname,
                    athlete.date_of_birth,
                    athlete.index_number,
                ])

    return response



def prepare_certificate(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    officials = school_official.objects.filter(school=team.school).exclude(status="Inactive")
    return render(request, "reports/off.html", {"officials": officials, "team": team})

def prepare_accreditation(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    officials = school_official.objects.filter(school=team.school).exclude(status="Inactive")
    return render(request, "reports/accreff.html", {"officials": officials, "team": team})
    # return render(request, "reports/accreff.html", {"officials": officials, "team": team})
    # return render(request, "reports/accreff.html", {"officials": officials, "team": team})
    # return render(request, "reports/accreff.html", {"officials": officials, "team": team})
    
def Aertificate(request, id):
    team = get_object_or_404(AthleticsEnrollment, id=id)
    athlete_enrollments = AthleticsAthletes.objects.filter(school_enrollment=team)
    athletes = Athlete.objects.filter(
        athleticsathletes__in=athlete_enrollments
    )

    # Get template
    template = get_template("reports/cert.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "team": team,
        "athletes": athletes,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    filename = f"{team.zone} | {team.sport} .pdf"
    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response


def AAcreditation(request, id):
    team = get_object_or_404(AthleticsEnrollment, id=id)
    athlete_enrollments = AthleticsAthletes.objects.filter(school_enrollment=team)
    athletes = Athlete.objects.filter(
        athleticsathletes__in=athlete_enrollments
    )

    # Get template
    template = get_template("athletics/acred.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
        "athletes": athletes,
        "team": team,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)
    filename = f"{team.zone} | {team.sport} .pdf"
    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response


def AAlbums(request, id):
    team = get_object_or_404(AthleticsEnrollment, id=id)
    athlete_enrollments = AthleticsAthletes.objects.filter(school_enrollment=team)
    today = date.today()
    athletes = Athlete.objects.filter(
        athleticsathletes__in=athlete_enrollments
    ).distinct().annotate(
        age=ExpressionWrapper(
            today.year - F('date_of_birth__year') -
            Case(
                When(date_of_birth__month__gt=today.month, then=Value(1)),
                When(
                    date_of_birth__month=today.month,
                    date_of_birth__day__gt=today.day,
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            ),
            output_field=IntegerField()
        )
    )

    # Get athlete and official counts
    athlete_count = athletes.count()
    # Create a unique filename
    filename = f"{team.zone} | {team.sport} .pdf"

    # Get template
    template = get_template("athletics/albums.html")

    # Prepare context
    context = {
        "team": team,
        "athlete_count": athlete_count,
        "athletes": athletes,
        "MEDIA_URL": settings.MEDIA_URL,
    }

    # Render HTML
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Generate PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response


def athletics_enroll_delete(request, id):
    stud = AthleticsEnrollment.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("athletics_enrollments")

    return render(request, "athletics/delete_athletics_enroll.html", {"obj": stud})


@login_required(login_url="login")
def remove_athletics(request, enrollment_id, athlete_id):
    athlete_enrollment = get_object_or_404(AthleticsAthletes, id=enrollment_id)
    athlete = get_object_or_404(Athlete, id=athlete_id)

    if request.method == "POST":
        athlete_enrollment.athletes.remove(athlete)
        return HttpResponseRedirect(
            reverse("athletics_enrollment", args=[athlete_enrollment.school_enrollment.id])
        )

    return redirect(
        "athletics_enrollment", id=athlete_enrollment.school_enrollment.id
    )

