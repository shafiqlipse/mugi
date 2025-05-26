from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from accounts.models import *
from accounts.forms import *
from .forms import *
from .filters import *
from django.contrib import messages
from accounts.decorators import *
import csv
from django.db import IntegrityError
from django.core.files.base import ContentFile
import base64
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from .models import Athlete, school_official
from django.core.cache import cache
import json
import requests
from django.conf import settings
from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.db.models import F
from enrollment.models import SchoolEnrollment
from django.contrib.auth import get_user_model

User = get_user_model()

@school_required
def Dash(request):
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

    return render(request, "dashboard/schoolview.html", context)



# schools

def users_data(request):
    """Handle AJAX DataTables request for large datasets"""
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get("search[value]", "").strip()

        # Filter base queryset
        users_query = User.objects.filter(is_school=True).select_related("school")

        # Apply search filters
        if search_value:
            users_query = users_query.filter(
                Q(username__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(school__name__icontains=search_value) |
                Q(school__emis_number__icontains=search_value)
            )

        # Pagination
        paginator = Paginator(users_query, length)
        page_number = (start // length) + 1
        users_page = paginator.get_page(page_number)

        data = []
        for user in users_page:
            school = getattr(user, 'school', None)
            name = school.name if school else "No School"
            emis = school.emis_number if school else "N/A"

            data.append({
                "username": user.username,
                "email": user.email,
                "school_profile": f"{name} | {emis}",
                "actions": f"""
                    <a href="/dashboard/user/edit/{user.id}/" class="btn btn-warning btn-sm">Edit</a>
                """,
            })

        response = {
            "draw": draw,
            "recordsTotal": User.objects.filter(is_school=True).count(),
            "recordsFiltered": users_query.count(),
            "data": data,
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# schools list, tuple or array
@staff_required
def users(request):
    
    users = User.objects.select_related("school").filter(is_school=True)

    context = {
        "users": users,
       
    }
    return render(request, "all/users.html", context)


# schools list, tuple or array

@staff_required
def school_data_view(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "").strip()

    # Filtering
    schools = School.objects.select_related("district__zone")

    if search_value:
        schools = schools.filter(
            Q(name__icontains=search_value) |
            Q(center_number__icontains=search_value) |
            Q(district__name__icontains=search_value) |
            Q(district__zone__name__icontains=search_value)
        )

    total_records = School.objects.count()
    filtered_records = schools.count()

    # Pagination
    paginator = Paginator(schools, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)

    # Build response data
    data = []
    for school in page.object_list:
        data.append({
            "id": school.id,
            "name": school.name,
            "center_number": school.center_number,
            "district": school.district.name if school.district else "",
            "zone": school.district.zone.name if school.district and school.district.zone else "",
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })
# @staff_required
@login_required(login_url="login")
def Schools(request):
    schools = School.objects.select_related("district__zone").order_by("-created")  # Remove slicing

    schools_filter = SchoolFilter(request.GET, queryset=schools)
    filtered_schools = schools_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_schools, 10)  # Show 10 schools per page
    page_number = request.GET.get("page")
    paginated_schools = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "schooles": paginated_schools,  # Ensure the correct variable name in the template
        "school_filter": schools_filter,
    }

    return render(request, "school/schools.html", context)


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



# schools list, tuple or array
@staff_required
def athlete_data_view(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = Athlete.objects.select_related('school').exclude(status="COMPLETED")

    total = queryset.count()

    if search_value:
        queryset = queryset.filter(
            Q(fname__icontains=search_value) |
            Q(lname__icontains=search_value) |
            Q(index_number__icontains=search_value) |
            Q(school__name__icontains=search_value)  # optionally include school name
        ) 

    filtered_total = queryset.count()

    data = list(
        queryset[start:start + length].values(
            'id',
            'fname',
            'lname',
            'index_number',
            'nationality',
            'gender',
            'status',
            'classroom',
            school_name=F('school__name'),
        )
    )

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_total,
        'data': data,
    })
    
    
def all_athletes(request):
    
    athletes_queryset = Athlete.objects.select_related("school").all().exclude(status="COMPLETED")

    context = {
        "athletes": athletes,

    }
    return render(request, "athletes/all_athletes.html", context)


# schools list, tuple or array

@staff_required
def archives_data_view(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = Athlete.objects.select_related("school").filter(status="COMPLETED")

    total = queryset.count()

    if search_value:
        queryset = queryset.filter(fname__icontains=search_value)  # or `lname`

    filtered_total = queryset.count()

    data = list(
        queryset[start:start + length].values(
            'id',
            'fname',
            'lname',
            'index_number',
            'nationality',
            'gender',
            'status',
            'classroom',
            school_name=F('school__name'),
        )
    )

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_total,
        'data': data,
    })
    
@staff_required
def archives(request):

    archives_list = Athlete.objects.select_related("school").filter(status="COMPLETED")
    # Apply filtering


    context = {
        "archives_list": archives_list,
    }
    return render(request, "athletes/archives.html", context)


# schools list, tuple or array
@staff_required
def all_officials(request):

    officilas = school_official.objects.select_related("school").all()

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

        return redirect(reverse('schooldetail', args=[id]))
    else:
        form = SchoolProfileForm(instance=school)
    context = {"form": form}
    return render(request, "school/create_school.html", context)


# @staff_required
@login_required(login_url="login")
def school_detail(request, id):
    school = get_object_or_404(School, id=id)
    officials = school_official.objects.select_related("school").filter(school_id=id)
    enrollments = SchoolEnrollment.objects.filter(school=school)
    athletes = Athlete.objects.select_related("school").filter(school_id=id).exclude(status="COMPLETED")

    context = {
        "school": school,
        "athletes": athletes,
        "officials": officials,
        "enrollments": enrollments,
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


import io
import logging
from django.core.cache import cache
logger = logging.getLogger(__name__)

@login_required(login_url="login")
def newAthlete(request):
    if request.method == "POST" and request.FILES.get("cropped_photo"):
        form = NewAthleteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_athlete = form.save(commit=False)
                    new_athlete.school = request.user.school
                    new_athlete.photo = request.FILES["cropped_photo"]


                    new_athlete.save()
                    messages.success(request, "Athlete added successfully!")
                    return redirect('athletes')  # Redirect to your athlete list view

            except IntegrityError:
                messages.error(request, "Index number already exists")
            except Exception as e:
                messages.error(request, f"Server error: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    # GET request or form errors
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




# # Athletes details......................................................
@login_required
def AthleteDetail(request, id):
    # Fetch the athlete object or return a 404 error
    athlete = get_object_or_404(Athlete, id=id)
    
    # Initialize variables
    new_screen = None
    dform = ScreenForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and dform.is_valid():
        # Save the form and associate it with the athlete and user
        new_screen = dform.save(commit=False)
        new_screen.athlete = athlete
        new_screen.screener = request.user
        new_screen.save()

        # Update athlete status to COMPLETED
        athlete.status = "COMPLETED"
        athlete.save()

        # Redirect to the athlete detail page
        return HttpResponseRedirect(reverse("athlete", args=[athlete.id]))

    # Calculate the athlete's age
    today = datetime.date.today()
    age = (
        today.year
        - athlete.date_of_birth.year
        - ((today.month, today.day) < (athlete.date_of_birth.month, athlete.date_of_birth.day))
    )

    context = {
        "athlete": athlete,
        "age": age,  # Pass the calculated age to the template
        "dform": dform,  # Pass the form to the template
    }

    return render(request, "athletes/athlete.html", context)


@login_required(login_url="login")
def athletes(request):
    user = request.user

    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "athletes/athletes.html", {"athletes": []})

    athletes = (
        Athlete.objects
        .filter(school=school_profile)
        .exclude(status="COMPLETED")
        .values("id", "fname", "lname", "index_number","date_of_birth", "gender","classroom")  # Fetch only id and name
    )

    return render(request, "athletes/athletes.html", {"athletes": athletes})

def red_athletes(request):
    user = request.user
    
    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "athletes/athletes.html", {"athletes": []})

    athletes = (
        Athlete.objects
        .filter(school=school_profile, status="ACTIVE")
         .values("id", "fname", "lname", "index_number","date_of_birth", "gender","classroom")  # Fetch only id and name
    )
    

    context = {
        "athletes": athletes,
    }

    return render(request, "athletes/dathletes.html", context)


@login_required(login_url="login")
def school_offs(request):
    user = request.user

    # Check if the user has a school profile
    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "officials/officials.html", {"school_offs": []})
        # Fetch school officials for the user's school, excluding inactive ones
    school_offs = (
            school_official.objects
            .select_related("school")  # Optimize by fetching school data in one query
            .filter(school=user.school)  # Directly filter by the school object
            .exclude(status="Inactive")  # Exclude inactive officials
        )

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
    screens = Screening.objects.select_related("athlete").all()
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
    athletes = Athlete.objects.select_related("school").all()
    context = {"athletes": athletes}
    return render(request, "school/athlete_list.html", context)


# def payment_page(request):
#     payment = Payment.objects.filter(is_paid=False).first()
@login_required
def activate_official(request, id):
    official = get_object_or_404(school_official,id=id)
    official.status = "Active"
    official.save() # Save the updated status
    messages.success(request, f"Official {official.fname} is now {official.status}.")
    return redirect("officials")
#     context = {"payment": payment}

@login_required
def deactivate_official(request, id):
    official = get_object_or_404(school_official,id=id)
    official.status = "Inactive"
    official.save() # Save the updated status
    messages.error(request, f"Official {official.fname} has been deleted successfully.")
    return redirect("officials")
#     context = {"payment": payment}







logger = logging.getLogger(__name__)

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
def generate_unique_transaction_id():
    while True:
        transaction_id = str(random.randint(10**11, 10**12 - 1))
        if not Payment.objects.filter(transaction_id=transaction_id).exists():
            return transaction_id

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def payment_view(request):
    school = request.user.school  # Get the logged-in user's school

    if request.method == 'POST':
        form = PaymentForm(request.POST, school=school)
        if form.is_valid():
            try:
                phone_number = form.cleaned_data['phone_number']
                athletes = form.cleaned_data['athletes']

                if not athletes:
                    messages.error(request, "You must select at least one athlete.")
                    return render(request, 'emails/payment_form.html', {'form': form})

                # Calculate total amount
                amount_per_athlete = 3000  # UGX 6,000 per athlete
                total_amount = (athletes.count() * amount_per_athlete) + 500  # UGX 500 additional fee

                with transaction.atomic():  # Ensures atomicity in case of failure
                    payment = Payment.objects.create(
                        school=school,
                        amount=total_amount,
                        phone_number=phone_number,
                    )
                    payment.athletes.set(athletes)  # Associate selected athletes with the payment

                messages.success(request, f"Payment of UGX {total_amount} successful!")
                logger.info(f"Payment successful: School={school}, Amount={total_amount}, Phone={phone_number}")

                return redirect('payment', payment.id)

            except Exception as e:
                logger.error(f"Payment failed for {school}: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred while processing the payment. Please try again.")

    else:
        form = PaymentForm(school=school)

    return render(request, 'emails/payment_form.html', {'form': form})

def get_airtel_token():
    """
    Retrieve Airtel Money OAuth token.
    """
    try:
        url = "https://openapi.airtel.africa/auth/oauth2/token"
        headers = {"Content-Type": "application/json", "Accept": "*/*" }
        payload = {
            "client_id": settings.AIRTEL_MONEY_CLIENT_ID,
            "client_secret": settings.AIRTEL_MONEY_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

        response = requests.post(url, json=payload, headers=headers, params={})
        logger.info(f"Token Response: {response.status_code}, {response.text}")
        print(response.json())
        if response.status_code == 200:
            return response.json().get("access_token")

        # Handle common errors
        error_response = response.json()
        error_message = error_response.get("error_description", error_response.get("message", "Unknown error"))

        if response.status_code == 400:
            logger.error("Invalid request format. Check parameters.")
            return None
        elif response.status_code == 401:
            logger.error("Authentication failed. Check your API credentials.")
            return None
        elif response.status_code == 403:
            logger.error("Permission denied. Your account may not have access.")
            return None
        elif response.status_code == 500:
            logger.error("Airtel Money server error. Try again later.")
            return None

        logger.error(f"Failed to get token: {error_message}")
        return None

    except requests.exceptions.ConnectionError:
        logger.error("Network error: Unable to reach Airtel Money API.")
        return None
    except requests.exceptions.Timeout:
        logger.error("Request timed out: Airtel Money API took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected request error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unknown error: {str(e)}")
        return None

import random
from django.db import transaction as db_transaction

def generate_unique_transaction_id():
    """Generate a unique 12-digit transaction ID."""
    while True:
        transaction_id = str(random.randint(10**11, 10**12 - 1))  # 12-digit random number
        if not Payment.objects.filter(transaction_id=transaction_id).exists():  # Ensure uniqueness
            return transaction_id


def initiate_payment(request, id):
    payment = get_object_or_404(Payment, id=id)
    
    try:
        token = get_airtel_token()  
        if not token:
            return JsonResponse({"error": "Failed to get authentication token"}, status=500)

        payment_url = "https://openapi.airtel.africa/merchant/v2/payments/"
        transaction_id = generate_unique_transaction_id()  


        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Country": "UG",
            "X-Currency": "UGX",
            "Authorization": f"Bearer {token}",
            "x-signature": settings.AIRTEL_API_SIGNATURE,  # Ensure this is set in settings.py
            "x-key": settings.AIRTEL_API_KEY,  # Ensure this is set in settings.py
        }

        payload = {
            "reference": str(payment.transaction_id),  # Use the Payment ID as the reference
            "subscriber": {
                "country": "UG",
                "currency": "UGX",
                "msisdn": re.sub(r"\D", "", str(payment.phone_number)).lstrip('0'),   # Remove non-numeric characters
            },
            "transaction": {
                "amount": float(payment.amount),  # Convert DecimalField to float
                "country": "UG",
                "currency": "UGX",
                "id": transaction_id,  # Use the generated transaction ID
            }
        }

        response = requests.post(payment_url, json=payload, headers=headers)
        logger.info(f"Payment Response: {response.status_code}, {response.text}")

       # Update payment record with transaction ID and set status to PENDING
        with db_transaction.atomic():
            payment.transaction_id = transaction_id
            payment.status = "PENDING"  # Set status to pending until confirmed
            payment.save()

        if response.status_code == 200:
            return redirect(reverse('payment_success', args=[payment.transaction_id]))  # ✅ Redirect to success page
        else:
            return JsonResponse({"error": "Failed to initiate payment", "details": response.text}, status=400)

    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
   
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import Payment  # Use the Payment model

airtel_logger = logging.getLogger('airtel_callback')  # Use the specific logger

@csrf_exempt
def airtel_payment_callback(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        # Log raw request body
        raw_body = request.body.decode('utf-8')
        airtel_logger.info(f"🔔 Airtel Callback Received: {raw_body}")

        # Parse JSON payload
        payload = json.loads(raw_body)
        airtel_logger.info(f"📜 Parsed JSON Payload:\n{json.dumps(payload, indent=2)}")

        # Extract transaction details
        transaction = payload.get("transaction", {})
        transaction_id = transaction.get("id")
        status_code = transaction.get("status_code")
        airtel_money_id = transaction.get("airtel_money_id")
        
        
        # Find the Payment record using transaction_id
        payment = get_object_or_404(Payment, transaction_id=transaction_id)

        # Map Airtel status to our system status
        status_mapping = {
            "TS": "COMPLETED",  # Transaction Successful
            "TF": "FAILED",      # Transaction Failed
            "TP": "PENDING",     # Transaction Pending
        }

        # Update payment status
        new_status = status_mapping.get(status_code, "FAILED")  # Default to FAILED if unknown status
        payment.status = new_status
        payment.save()

        airtel_logger.info(f"📌 Transaction ID: {transaction_id}, Status Code: {status_code}, Airtel Money ID: {airtel_money_id}")

        return JsonResponse({"message": "Callback received successfully"}, status=200)

    except json.JSONDecodeError:
        airtel_logger.error("❌ Invalid JSON received in callback")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        airtel_logger.error(f"❌ Error processing callback: {str(e)}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)
    
    

    
    
    
def payment_success(request, transaction_id):
    payment = Payment.objects.filter(transaction_id=transaction_id).first()
    
    if not payment:
        return render(request, 'payment_failed.html', {'error': 'Transaction not found'})

    return render(request, 'emails/payment_success.html', {
        'amount': payment.amount,
        'transaction_id': payment.transaction_id,
        'timestamp': payment.created_at,  # Make sure your Payment model has `created_at`
    })
    
  