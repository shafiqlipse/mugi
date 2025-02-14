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

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


from .filters import SchoolEnrollmentFilter  # Assume you have created this filter


def SchoolEnrollments(request):
    # Get school from user profile
    school = request.user.school  # Assuming profile has school attribute

    # Get all enrollments for the school
    enrollments = SchoolEnrollment.objects.filter(school=school)

    if request.method == "POST":
        form = SchoolEnrollmentForm(request.POST, request.FILES)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.school = school
            enrollment.save()
            messages.success(request, "Enrollment created successfully!")
            return redirect("school_enrollments")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolEnrollmentForm()

    context = {"form": form, "enrollments": enrollments}
    return render(request, "enrollments/school_enrolls.html", context)


def AllEnrollments(request):
    # Get all school_enrolls
    school_enrolls = SchoolEnrollment.objects.all()

    # Apply the filter
    # school_enroll_filter = SchoolEnrollmentFilter(request.GET, queryset=school_enrolls)
    # filtered_school_enrolls = school_enroll_filter.qs

    # Prepare context with athletes data
    context = {
        "school_enrolls": school_enrolls,
    }

    return render(request, "enrollments/enroll.html", context)


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


def school_enrollment_details(request, id):
    school_enrollment = get_object_or_404(SchoolEnrollment, id=id)
    school = school_enrollment.school
    if request.method == "POST":
        form = AthleteEnrollmentForm(request.POST)
        if form.is_valid():
            athlete_enrollment = AthleteEnrollment.objects.create(
                school_enrollment=school_enrollment
            )
            athlete_enrollment.athletes.set(form.cleaned_data["athletes"])
            return HttpResponseRedirect(reverse("school_enrollment", args=[id]))
    else:
        form = AthleteEnrollmentForm()

    athlete_enrollments = AthleteEnrollment.objects.filter(
        school_enrollment=school_enrollment
    )
    all_athletes = Athlete.objects.filter(school=school, status="NEW")

    context = {
        "school_enrollment": school_enrollment,
        "form": form,
        "athlete_enrollments": athlete_enrollments,
        "all_athletes": all_athletes,
    }
    return render(request, "enrollments/school_enroll.html", context)


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


def Accreditation(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    athlete_enrollments = AthleteEnrollment.objects.filter(school_enrollment=team)
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

def Occreditation(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    
    officials = school_official.objects.filter(school=team.school)

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
    officials = school_official.objects.filter(school=school)

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


def Certificate(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    athlete_enrollments = AthleteEnrollment.objects.filter(school_enrollment=team)
    athletes = Athlete.objects.filter(athleteenrollment__in=athlete_enrollments)

    # Get template
    template = get_template("reports/cert.html")

    # Compress and fix rotation for athletes' photos

    # Prepare context
    context = {
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


def Cortificate(request, id):
    team = get_object_or_404(SchoolEnrollment, id=id)
    
    officials = school_official.objects.filter(school=team.school)

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
