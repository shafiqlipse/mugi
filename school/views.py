from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from accounts.models import *
from accounts.forms import *
from .models import User
from .forms import *
from accounts.forms import *
from django.contrib import messages
from accounts.decorators import *
import csv
from django.db import IntegrityError
from django.core.files.base import ContentFile
import base64
from django.core.paginator import Paginator


@school_required
def Dash(request):
    school = request.user.school

    athletes = Athlete.objects.filter(school=school)[:6]
    athletes_count = Athlete.objects.filter(school=school).count
    officials_count = school_official.objects.all().count
    athletes_bcount = Athlete.objects.filter(gender="male").count
    athletes_gcount = Athlete.objects.filter(gender="female").count
    officials_bcount = school_official.objects.filter(gender="M").count
    officials_gcount = school_official.objects.filter(gender="F").count
    context = {
        "athletes": athletes,
        "athletes_count": athletes_count,
        "athletes_bcount": athletes_bcount,
        "athletes_gcount": athletes_gcount,
        "officials_count": officials_count,
        "officials_bcount": officials_bcount,
        "officials_gcount": officials_gcount,
    }
    return render(request, "dashboard/schoolview.html", context)


# schools


# schools list, tuple or array
@staff_required
def users(request):
    staff = User.objects.all().exclude(is_school=True)
    users = User.objects.filter(is_school=True)

    context = {
        "users": users,
        "staff": staff,
        # "teamsFilter": teams
    }
    return render(request, "all/users.html", context)


# schools list, tuple or array
# @staff_required
@login_required(login_url="login")
def Schools(request):

    schools = School.objects.all()

    context = {
        "schools": schools,
        # "teamsFilter": teams
    }
    return render(request, "school/schools.html", context)

    # schools list, tuple or array


@login_required(login_url="login")
def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="schools.csv"'

    writer = csv.writer(response)
    writer.writerow(["School Name", "emis_number", "Contact", "Zone"])  # CSV header

    # Fetch data from the database and write it to the CSV file
    schools = School.objects.all()
    for school in schools:
        writer.writerow(
            [school.name, school.emis_number, school.phone_number, school.zone]
        )

    return response


@login_required(login_url="login")
def exportp_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="schools.csv"'

    writer = csv.writer(response)
    writer.writerow(["School Name", "EMIS", "Contact", "District"])  # CSV header

    # Fetch data from the database and write it to the CSV file
    schools = School.objects.filter(status="Active")
    for school in schools:
        writer.writerow(
            [school.school_name, school.EMIS, school.phone_number, school.district]
        )

    return response


from .filters import AthleteFilter


# schools list, tuple or array
@staff_required
def all_athletes(request):
    # Query all athletes except those with status "COMPLETED"
    athletes_queryset = Athlete.objects.all().exclude(status="COMPLETED")

    # Apply filtering
    athlete_filter = AthleteFilter(request.GET, queryset=athletes_queryset)
    filtered_athletes = athlete_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_athletes, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_athletes = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "athletes": paginated_athletes,
        "athlete_filter": athlete_filter,
    }
    return render(request, "athletes/all_athletes.html", context)


# schools list, tuple or array
@staff_required
def archives(request):
    archives_list = Athlete.objects.filter(status="COMPLETED")
    paginator = Paginator(archives_list, 10)  # Show 10 athletes per page.

    page_number = request.GET.get("page")
    athletes = paginator.get_page(page_number)

    context = {
        "athletes": athletes,
    }
    return render(request, "athletes/archives.html", context)


# schools list, tuple or array
@staff_required
def all_officials(request):

    officilas = school_official.objects.all()

    context = {
        "officilas": officilas,
    }
    return render(request, "officials/allofficials.html", context)


def school_new(request):
    if request.method == "POST":
        form = SchoolProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                school = form.save(commit=False)

                # Handle cropped and resized images
                for field in ["badge", "photo", "gphoto"]:
                    cropped_data = request.POST.get(f"{field}_cropped")
                    if cropped_data:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"{field}.{ext}"
                        )
                        setattr(school, field, data)

                school.save()
                messages.success(request, "School profile created successfully!")
                return redirect("confirm")
            except IntegrityError as e:
                if "EMIS" in str(e):
                    messages.error(
                        request, "A school with this EMIS number already exists."
                    )
                else:
                    messages.error(
                        request,
                        "An error occurred while saving the school. Please fill all required fields.",
                    )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SchoolProfileForm()

    regions = Region.objects.all()
    context = {
        "form": form,
        "regions": regions,
    }
    return render(request, "school/create_school.html", context)


@login_required
def schoolupdate(request, id):
    school = School.objects.get(id=id)

    if request.method == "POST":
        form = SchoolProfileForm(request.POST, instance=school)
        if form.is_valid():
            form.save()

            return redirect("school_dashboard")
    else:
        form = SchoolProfileForm(instance=school)
    context = {"form": form}
    return render(request, "school/create_school.html", context)


# @staff_required
@login_required(login_url="login")
def school_detail(request, id):
    school = get_object_or_404(School, id=id)
    officials = school_official.objects.filter(school_id=id)
    athletes = Athlete.objects.filter(school_id=id)

    context = {
        "school": school,
        "athletes": athletes,
        "officials": officials,
    }
    return render(request, "school/school.html", context)


# schools list, tuple or array
@school_required
def Official(request):

    if request.method == "POST":
        form = OfficialForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                official = form.save(commit=False)

                # Assign the school from the user profile
                official.school = request.user.school

                # Handle cropped image data for the "photo" field
                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        official.photo = data  # Assign cropped image
                    except (ValueError, TypeError) as e:
                        messages.error(request, "Invalid image data.")
                        return render(
                            request, "officials/NOfficials.html", {"form": form}
                        )

                official.save()
                messages.success(request, "official added successfully!")
                return redirect("officials")

            except IntegrityError as e:
                if "lin" in str(e).lower():
                    messages.error(
                        request,
                        "An official with this Learner Identification Number (LIN) already exists.",
                    )
                else:
                    messages.error(request, f"Error adding official: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error adding official: {str(e)}")
        else:
            # Form validation error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = OfficialForm()
    context = {"form": form}
    return render(request, "officials/NOfficial.html", context)


@login_required(login_url="login")
def newAthlete(request):
    if request.method == "POST":
        form = NewAthleteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_athlete = form.save(commit=False)

                # Assign the school from the user profile
                new_athlete.school = request.user.school  # Ensure profile has a school

                # Handle cropped image data for the "photo" field
                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        new_athlete.photo = data  # Assign cropped image
                    except (ValueError, TypeError) as e:
                        messages.error(request, "Invalid image data.")
                        return render(
                            request, "athletes/new_athletes.html", {"form": form}
                        )

                new_athlete.save()
                messages.success(request, "Athlete added successfully!")
                return redirect("athletes")

            except IntegrityError as e:
                if "lin" in str(e).lower():
                    messages.error(
                        request,
                        "An athlete with this Learner Identification Number (LIN) already exists.",
                    )
                else:
                    messages.error(request, f"Error adding athlete: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error adding athlete: {str(e)}")
        else:
            # Form validation error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = NewAthleteForm()

    return render(request, "athletes/new_athletes.html", {"form": form})


# a confirmation of credentials
# @login_required
def confirmation(request):
    user = request.user
    context = {"user": user}
    return render(request, "confirm.html", context)


def offcom(request):
    user = request.user
    context = {"user": user}
    return render(request, "offcom.html", context)


def ofifcom(request):
    user = request.user
    context = {"user": user}
    return render(request, "ofifcom.html", context)


import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse


# # Athletes details......................................................
@login_required
def AthleteDetail(request, id):
    athlete = get_object_or_404(Athlete, id=id)
    relatedathletes = Athlete.objects.filter(
        school=athlete.school, sport=athlete.sport
    ).exclude(id=id)[:3]
    new_screen = None
    user = request.user
    if request.method == "POST":
        dform = ScreenForm(request.POST, request.FILES)

        if dform.is_valid():
            new_screen = dform.save(commit=False)
            new_screen.athlete = athlete
            new_screen.screener = user
            new_screen.save()

            # Update athlete status to COMPLETED
            athlete.status = "COMPLETED"
            athlete.save()

            return HttpResponseRedirect(reverse("athlete", args=[athlete.id]))
    else:
        dform = ScreenForm()

    # Calculate the athlete's age
    today = datetime.date.today()
    age = (
        today.year
        - athlete.date_of_birth.year
        - (
            (today.month, today.day)
            < (athlete.date_of_birth.month, athlete.date_of_birth.day)
        )
    )

    context = {
        "athlete": athlete,
        "relatedathletes": relatedathletes,
        "age": age,  # Pass the calculated age to the template
        "dform": dform,  # Add the form to the context
    }

    return render(request, "athletes/athlete.html", context)


@login_required(login_url="login")
def athletes(request):
    user = request.user
    school_profile = user.school  # Retrieve the first related School object
    school_id = school_profile.id
    athletes = Athlete.objects.filter(school_id=school_id).exclude(status="COMPLETED")

    context = {
        "athletes": athletes,
    }

    return render(request, "athletes/athletes.html", context)


@login_required(login_url="login")
def school_offs(request):
    user = request.user
    school_profile = user.school  # Retrieve the first related School object
    if school_profile:
        school_id = school_profile.id
        school_offs = school_official.objects.filter(school_id=school_id)
    else:
        # Handle the case where the user is not associated with any school
        school_offs = school_official.objects.none()
    # officialFilter = OfficialFilter(request.GET, queryset=officials)

    context = {
        "school_offs": school_offs,
    }

    return render(request, "officials/officials.html", context)


@login_required
def AthleteUpdate(request, id):
    athlete = get_object_or_404(Athlete, id=id)

    if request.method == "POST":
        form = NewAthleteForm(request.POST, request.FILES, instance=athlete)
        if form.is_valid():
            try:
                new_athlete = form.save(commit=False)

                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        new_athlete.photo = data  # Assign cropped image
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "trainee_new.html", {"form": form})

                new_athlete.save()
                messages.success(
                    request,
                    "Updated successfully! ",
                )
                return redirect("allathletes")

            except IntegrityError:
                messages.error(request, "There was an error saving the trainee.")
                return render(request, "trainee_new.html", {"form": form})

    else:
        form = NewAthleteForm(instance=athlete)

    context = {
        "form": form,
        "athlete": athlete,
    }
    return render(request, "athletes/new_athletes.html", context)


# # Athletes details......................................................
@staff_required
def Screened(request):
    screens = Screening.objects.all()
    context = {"screens": screens}
    return render(request, "athletes/screens.html", context)


# # Athletes details......................................................
@admin_required(login_url="login")
def DeleteAthlete(request, id):
    stud = Athlete.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("allathletes")

    return render(request, "athletes/delete_ath.html", {"obj": stud})


# # Athletes details......................................................
@admin_required(login_url="login")
def DeleteOfficial(request, id):
    stud = school_official.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("officials")

    return render(request, "officials/delete_off.html", {"obj": stud})


# # Athletes details......................................................
@login_required(login_url="login")
def DeleteSchool(request, id):
    stud = School.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("schools")

    return render(request, "school/deletesch.html", {"obj": stud})


# # Athletes details......................................................
@login_required(login_url="login")
def OfficialDetail(request, id):
    official = get_object_or_404(school_official, id=id)
    relatedathletes = school_official.objects.filter(school=official.school).exclude(
        id=id
    )

    context = {
        "official": official,
        "relatedathletes": relatedathletes,
        # "breadcrumbs": breadcrumbs,
    }

    return render(request, "officials/official.html", context)


@login_required(login_url="login")
def athlete_list(request):
    athletes = Athlete.objects.all()
    context = {"athletes": athletes}
    return render(request, "school/athlete_list.html", context)


# def payment_page(request):
#     payment = Payment.objects.filter(is_paid=False).first()
#     context = {"payment": payment}
#     return render(request, "school/payment_page.html", context)


# import requests
# from django.conf import settings


# def initiate_payment(request):
#     # Retrieve Airtel Money credentials from settings
#     client_id = settings.AIRTEL_MONEY_CLIENT_ID
#     client_secret = settings.AIRTEL_MONEY_CLIENT_SECRET

#     # Your payment initiation logic here
#     # Make requests to Airtel Money API using client_id, client_secret, etc.
#     # Example:
#     response = requests.post(
#         "https://openapiuat.airtel.africa/",
#         data={
#             "client_id": client_id,
#             "client_secret": client_secret,
#         },
#     )

#     # Process the response and handle accordingly
#     # Example:
#     if response.status_code == 200:
#         return HttpResponse("Payment initiated successfully")
#     else:
#         return HttpResponse("Failed to initiate payment")

import csv
from django.http import HttpResponse


def export_scsv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'

    # Create a CSV writer object using the HttpResponse as the file.
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "Name",
            "District",
            "Zone",
            "Region",
         
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in School.objects.all():
        writer.writerow(
            [
                
                obj.name,
                obj.district,
                obj.district.zone,
                obj.district.zone.region,
            ]
        )  # Replace with your model's fields

    return response
