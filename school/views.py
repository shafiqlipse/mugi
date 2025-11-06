from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from accounts.models import *
from accounts.forms import *
from transfers.models import TransferPayment
from training.models import Trainee
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
import io
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import Payment  # Use the Payment model
import random
from django.db import transaction as db_transaction

logger = logging.getLogger(__name__)
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
            'gender',
            'id',
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
    return render(request, "school/newschool.html", context)


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

@login_required
def request_athlete_edit(request, athlete_id):
    athlete = get_object_or_404(Athlete, id=athlete_id)
    school = request.user.school

    if request.method == 'POST':
        try:
            # Collect the proposed changes
            requested_changes = {}
            original_data = {}
            for field in ['fname', 'lname', 'mname', 'index_number', 'lin', 'date_of_birth', 'gender', 'photo']:
                new_value = request.FILES.get(field) or request.POST.get(field)
                old_value = getattr(athlete, field)

                if hasattr(old_value, 'name'):
                    old_value = old_value.name

                if new_value and str(new_value) != str(old_value):
                    requested_changes[field] = str(new_value)
                    original_data[field] = str(old_value)

            phone_number = request.POST.get('phone_number')
            reason = request.POST.get('reason')
            supporting_doc = request.FILES.get('supporting_document')

            # Validate phone number
            if not re.match(r'^(075|074|070)\d{7}$', phone_number):
                messages.error(request, "Phone number must be a valid Airtel number (070, 074, or 075).")
                return render(request, 'athletes/request_edit.html', {'athlete': athlete})

            # Calculate fee (you can adjust this)
            amount = 50000  

            with transaction.atomic():
                edit_request = AthleteEditRequest.objects.create(
                    athlete=athlete,
                    school=school,
                    requested_by=request.user,
                    reason=reason,
                    supporting_document=supporting_doc,
                    requested_changes=requested_changes,
                    original_data=original_data,
                    phone_number=phone_number,
                    amount=amount,
                    transaction_id=str(random.randint(10**11, 10**12 - 1)),
                    status='PENDING',
                )

            # Get Airtel token
            token = get_airtel_token()
            if not token:
                messages.error(request, "Failed to connect to Airtel. Please try again later.")
                return render(request, 'athletes/request_edit.html', {'athlete': athlete})

            # Prepare Airtel API request
            payment_url = "https://openapi.airtel.africa/merchant/v2/payments/"
            msisdn = re.sub(r"\D", "", str(phone_number)).lstrip('0')

            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "X-Country": "UG",
                "X-Currency": "UGX",
                "Authorization": f"Bearer {token}",
                "x-signature": settings.AIRTEL_API_SIGNATURE,
                "x-key": settings.AIRTEL_API_KEY,
            }

            payload = {
                "reference": str(edit_request.transaction_id),
                "subscriber": {
                    "country": "UG",
                    "currency": "UGX",
                    "msisdn": msisdn,
                },
                "transaction": {
                    "amount": float(amount),
                    "country": "UG",
                    "currency": "UGX",
                    "id": edit_request.transaction_id,
                },
            }

            # Send payment request
            response = requests.post(payment_url, json=payload, headers=headers)
            logger.info(f"Airtel Payment Response ({response.status_code}): {response.text}")

            if response.status_code == 200:
                messages.success(
                    request,
                    f"Edit request submitted successfully! Please confirm Airtel payment of UGX {amount}."
                )
                return redirect('edit_request_detail', request_id=edit_request.id)
            else:
                edit_request.status = "FAILED"
                edit_request.save()
                messages.error(request, "Payment initiation failed. Please try again.")
                return render(request, 'athletes/request_edit.html', {'athlete': athlete})

        except Exception as e:
            logger.error(f"❌ Error processing athlete edit request: {str(e)}", exc_info=True)
            messages.error(request, "An error occurred while submitting your request. Please try again.")

    return render(request, 'athletes/request_edit.html', {'athlete': athlete})

def edit_request_success(request):
    return render(request, 'athletes/edit_request_success.html')

def edit_requests_list(request):
    requests = AthleteEditRequest.objects.select_related('athlete', 'requested_by', 'school').all()
    return render(request, 'athletes/edit_requests_list.html', {'requests': requests})



def edit_request_detail(request, request_id):
    edit_request = get_object_or_404(AthleteEditRequest, id=request_id)
    athlete = edit_request.athlete

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            # Apply approved changes
            for field, new_value in edit_request.requested_changes.items():
                if field == 'photo':
                    # Skip photo updates (can be handled manually)
                    continue
                setattr(athlete, field, new_value)
            athlete.save()

            edit_request.status = 'APPROVED'
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()

            messages.success(request, "Edit request approved and changes applied.")
            return redirect('edit_requests_list')

        elif action == 'reject':
            edit_request.status = 'REJECTED'
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()

            messages.info(request, "Edit request rejected.")
            return redirect('edit_requests_list')

        elif action == 'pay':
            # Handle payment initiation for edit requests
            phone_number = edit_request.phone_number
            if not phone_number:
                messages.error(request, "Phone number missing for this request.")
                return redirect('edit_request_detail', request_id=edit_request.id)

            try:
                # 💰 Payment details
                amount = 5000  # e.g., edit request fee
                edit_request.amount = amount
                edit_request.transaction_id = str(random.randint(10**11, 10**12 - 1))
                edit_request.status = "PENDING"
                edit_request.save()

                # 🔐 Get Airtel token
                token = get_airtel_token()
                if not token:
                    messages.error(request, "Failed to connect to Airtel. Try again later.")
                    return redirect('edit_request_detail', request_id=edit_request.id)

                # 🌍 Airtel API setup
                payment_url = "https://openapi.airtel.africa/merchant/v2/payments/"
                msisdn = re.sub(r"\D", "", str(phone_number)).lstrip('0')

                headers = {
                    "Accept": "*/*",
                    "Content-Type": "application/json",
                    "X-Country": "UG",
                    "X-Currency": "UGX",
                    "Authorization": f"Bearer {token}",
                    "x-signature": settings.AIRTEL_API_SIGNATURE,
                    "x-key": settings.AIRTEL_API_KEY,
                }

                payload = {
                    "reference": str(edit_request.transaction_id),
                    "subscriber": {
                        "country": "UG",
                        "currency": "UGX",
                        "msisdn": msisdn,
                    },
                    "transaction": {
                        "amount": float(amount),
                        "country": "UG",
                        "currency": "UGX",
                        "id": edit_request.transaction_id,
                    },
                }

                response = requests.post(payment_url, json=payload, headers=headers)
                logger.info(f"Airtel Payment Response ({response.status_code}): {response.text}")

                if response.status_code == 200:
                    messages.success(
                        request,
                        f"Payment initiated successfully! Please confirm UGX {amount} on your Airtel line."
                    )
                else:
                    messages.error(request, "Payment initiation failed. Please try again.")

                return redirect('edit_request_detail', request_id=edit_request.id)

            except Exception as e:
                logger.error(f"❌ Error during edit request payment: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred while processing your payment.")
                return redirect('edit_request_detail', request_id=edit_request.id)

    # Default GET request
    return render(request, 'athletes/edit_request_detail.html', {'edit_request': edit_request})


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

    # Get athlete IDs that have pending or paid edit requests
    # requested_athletes = AthleteEditRequest.objects.filter(
    #     school=school_profile,
    #     status__in=["APPROVED", "PAID"]
    # ).values_list("athlete_id", flat=True)

    # Exclude those athletes from the queryset
    athletes = (
        Athlete.objects
        .filter(school=school_profile)
        .exclude(status="COMPLETED")
        .values("id", "fname", "lname", "index_number", "date_of_birth", "gender", "classroom")
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

def update_official(request, id):
    official = get_object_or_404(school_official, id=id)
    original_school = official.school # Store the original school for validation
    if request.method == "POST":
        form = OfficialForm(request.POST, request.FILES, instance=official)
        if form.is_valid():
            try:
                updated_official = form.save(commit=False)

                # Ensure the school is set to current user's school
                updated_official.school = original_school

                # Handle cropped image data if present
                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        updated_official.photo = data
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "officials/NOfficial.html", {"form": form, "update": True})

                updated_official.save()
                messages.success(request, "Official updated successfully!")
                return redirect("officials")

            except IntegrityError as e:
                if "nin" in str(e).lower():
                    messages.error(request, "An official with this NIN already exists.")
                else:
                    messages.error(request, f"Integrity error: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error updating official: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = OfficialForm(instance=official)

    return render(request, "officials/NOfficial.html", {"form": form, "update": True})



@login_required
def AthleteUpdate(request, id):
    athlete = get_object_or_404(Athlete, id=id)

    if request.method == "POST":
        form = NewAthleteForm(request.POST, request.FILES, instance=athlete)
        if form.is_valid():
            try:
                new_athlete = form.save(commit=False)

                # Handle cropped photo from blob
                cropped_file = request.FILES.get("cropped_photo")
                if cropped_file:
                    new_athlete.photo = cropped_file

                new_athlete.save()
                messages.success(request, "Updated successfully!")
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
#     context = {"payment": payment}
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

#     context = {"payment": payment}
#     context = {"payment": payment}
#     context = {"payment": payment}
#     context = {"payment": payment}
def generate_unique_transaction_id():
    while True:
        transaction_id = str(random.randint(10**11, 10**12 - 1))
        if not Payment.objects.filter(transaction_id=transaction_id).exists():
            return transaction_id


logger = logging.getLogger(__name__)

def payment_view(request):
    school = request.user.school  # Get the logged-in user's school

    if request.method == 'POST':
        form = PaymentForm(request.POST, school=school)
        if form.is_valid():
            try:
                phone_number = form.cleaned_data['phone_number']
                athletes = form.cleaned_data['athletes']

# Validate phone number format
                if not re.match(r'^(075|074|070)\d{7}$', phone_number):
                    messages.error(request, "Phone number must a valid Airtel money number.")
                    return render(request, 'payments/payment_form.html', {'form': form})

                if not athletes:
                    messages.error(request, "You must select at least one athlete.")
                    return render(request, 'payments/payment_form.html', {'form': form})

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


airtel_logger = logging.getLogger('airtel_callback')  # Use the specific logger

@csrf_exempt
def airtel_payment_callback(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    try:
        raw_body = request.body.decode("utf-8")
        airtel_logger.info(f"🔔 Airtel Callback Received: {raw_body}")
        payload = json.loads(raw_body)

        transaction = payload.get("transaction", {})
        transaction_id = transaction.get("id")
        status_code = transaction.get("status_code")
        airtel_money_id = transaction.get("airtel_money_id")

        status_mapping = {"TS": "COMPLETED", "TF": "FAILED", "TP": "PENDING"}
        new_status = status_mapping.get(status_code, "FAILED")

        # --- Update Payment ---
        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if payment:
            payment.status = new_status
            payment.save()

        # --- Update Trainee and related TransferRequest ---
        trainee = get_object_or_404(Trainee, transaction_id=transaction_id)
        if trainee:
            trainee.payment_status = new_status
            if new_status == "COMPLETED":
                trainee.payment_status = 'Completed'  # ✅ Mark as paid
                airtel_logger.info(f"✅ Payment successful for {trainee.first_name} {trainee.last_name}")
            else:
                trainee.payment_status = 'Failed'
                airtel_logger.warning(f"⚠️ Payment not completed: {new_status} for {trainee.transaction_id}")

            trainee.save()

        # --- Update TransferPayment and related TransferRequest ---
        transfer_payment = TransferPayment.objects.filter(transaction_id=transaction_id).first()
        if transfer_payment:
            transfer_payment.status = new_status
            if new_status == "COMPLETED":
                transfer_payment.paid_at = timezone.now()
                if transfer_payment.transfer:
                    transfer_payment.transfer.status = "paid"
                    transfer_payment.transfer.save()
            transfer_payment.save()

        # --- Update AthleteEditRequest if exists ---
        edit_request = AthleteEditRequest.objects.filter(transaction_id=transaction_id).first()
        if edit_request:
            edit_request.status = new_status
            edit_request.save()

        airtel_logger.info(f"📌 Transaction ID: {transaction_id}, Status Code: {status_code}, Airtel Money ID: {airtel_money_id}")
        return JsonResponse({"message": "Callback processed"}, status=200)

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
    
  
import csv
from django.http import HttpResponse

def export_pcsv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="enrollments.csv"'

    writer = csv.writer(response)

    # Header row
    writer.writerow([
        "Payment ID",
        "School",
        "Athletes",
        "Phone Number",
        "Amount",
    ])

    for payment in Payment.objects.select_related("school").filter(status='COMPLETED'):
        athletes_count = payment.athletes.all().count()  # <-- Use parentheses to call count()
        writer.writerow([
            payment.transaction_id,
            payment.school.name,
            athletes_count,
            payment.phone_number,
            payment.amount,
        ])

    return response

from django.shortcuts import get_object_or_404
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io
from decimal import Decimal

def add_watermark(p, width, height):
    p.saveState()
    p.setFont("Helvetica-Bold", 60)
    p.setFillColorRGB(0.9, 0.9, 0.9)  # light gray
    p.translate(width / 2, height / 2)
    p.rotate(45)
    p.drawCentredString(0, 0, "USSSA RECEIPT")
    p.restoreState()

def generate_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    athletes = payment.athletes.all()
    athlete_count = athletes.count()
    unit_price = Decimal("3000")
    flat_fee = Decimal("500")
    subtotal = unit_price * athlete_count
    total = subtotal + flat_fee

    # Setup PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set margins
    left_margin = 0.5 * inch
    top_margin = height - 0.5 * inch
    line_height = 14
    
    # watermark
    add_watermark(p, width, height)

    # Logo and Company Info Header
    try:
        # Draw logo (adjust path to your actual logo file)
        logo_path = "https://reg.usssaonline.com/static/lib/images/logo-receipt-01.png"  # Replace with your logo path
        logo_width = 1.5 * inch
        logo_height = 0.95 * inch
        p.drawImage(logo_path, left_margin, top_margin - logo_height + 10, 
                   width=logo_width, height=logo_height, preserveAspectRatio=True)
        
        # Company info to the right of logo
        company_info_x = left_margin + 1.25 * inch
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(1.0, 0.0, 0.0)  # Dark blue color for title
        p.drawString(company_info_x, top_margin, "UGANDA SECONDARY SCHOOLS SPORTS ASSOCIATION")
        p.setFont("Helvetica", 10)
        top_margin -= line_height
        p.drawString(company_info_x, top_margin, "GNS PLAZA, OLD K'LA ROAD")
        top_margin -= line_height
        p.drawString(company_info_x, top_margin, "114052 KAMPALA UGANDA")
        top_margin -= line_height
        p.drawString(company_info_x, top_margin, "(256) 393-256054 | info@usssaonline.com")
        top_margin -= line_height
        p.drawString(company_info_x, top_margin, "www.usssaonline.com")
        
        # Adjust top margin to account for logo height
        top_margin = min(top_margin, height - 0.5 * inch - logo_height - 10)
    except:
        # Fallback if logo fails to load
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(0.2, 0.2, 0.6)  # Dark blue
        p.drawString(left_margin, top_margin, "UGANDA SECONDARY SCHOOLS SPORTS ASSOCIATION")
        p.setFont("Helvetica", 10)
        top_margin -= line_height
        p.drawString(left_margin, top_margin, "GNS PLAZA, OLD K'LA ROAD")
        top_margin -= line_height
        p.drawString(left_margin, top_margin, "114052 KAMPALA UGANDA")
        top_margin -= line_height
        p.drawString(left_margin, top_margin, "(256) 393-256054 | info@usssaonline.com")
        top_margin -= line_height
        p.drawString(left_margin, top_margin, "www.usssaonline.com")
    
    # Divider line
    top_margin -= line_height * 2.5
    # p.line(left_margin, top_margin, width - left_margin, top_margin)/
    top_margin -= line_height
    
    
    # Reset to black for subsequent text
    p.setFillColorRGB(0, 0, 0)
    
    # Recipient Info
    p.setFont("Helvetica-Bold", 12)
    p.setFillColorRGB(0.4, 0.4, 0.4)  # Dark gray for date
    p.drawString(left_margin, top_margin, "RECIPIENT:")
    top_margin -= line_height
    p.setFont("Helvetica", 10)
    p.drawString(left_margin, top_margin, payment.school.name)
    top_margin -= line_height
    p.drawString(left_margin, top_margin, f"Address: {payment.school.district.zone} {payment.school.district}")
    top_margin -= line_height
    p.drawString(left_margin, top_margin, f"Phone: {payment.phone_number}")
    
    # Divider line
    top_margin -= line_height * 2.5
    # p.line(left_margin, top_margin, width - left_margin, top_margin)/
    top_margin -= line_height
    
    # Receipt Title
# Receipt Title (Right-aligned)
    p.setFont("Helvetica-Bold", 14)
    receipt_title = f"Receipt for #{payment.transaction_id or 'N/A'}"
    # Calculate width of text to right-align it
    title_width = p.stringWidth(receipt_title, "Helvetica-Bold", 14)
    p.drawString(width - left_margin - title_width, top_margin, receipt_title)
    top_margin -= line_height * 2

    p.setFont("Helvetica", 10)
    date_text = f"Transaction Date: {payment.created_at.strftime('%B %d, %Y')}"
    # Calculate width of date text to right-align it
    date_width = p.stringWidth(date_text, "Helvetica", 10)
    p.drawString(width - left_margin - date_width, top_margin, date_text)
    top_margin -= line_height * 2


    
    # Table Header
    p.setFont("Helvetica-Bold", 10)
    col_positions = [left_margin, left_margin + 2*inch, left_margin + 4*inch, left_margin + 5*inch, left_margin + 6*inch]
    p.drawString(col_positions[0], top_margin, "SERVICE")
    p.drawString(col_positions[1], top_margin, "DESCRIPTION")
    p.drawString(col_positions[2], top_margin, "QTY.")
    p.drawString(col_positions[3], top_margin, "COST")
    p.drawString(col_positions[4], top_margin, "TOTAL")
    top_margin -= line_height
    p.line(left_margin, top_margin, width - left_margin, top_margin)
    top_margin -= line_height
    
    # Table Row 1: Athlete Registration
    p.setFont("Helvetica", 10)
    p.drawString(col_positions[0], top_margin, "Athlete Registration")
    p.drawString(col_positions[1], top_margin, "Registration fees")
    p.drawString(col_positions[2], top_margin, str(athlete_count))
    p.drawString(col_positions[3], top_margin, f"UGX {unit_price:,.2f}")
    p.drawString(col_positions[4], top_margin, f"UGX {subtotal:,.2f}")
    top_margin -= line_height
    
    # Athlete Names (as description)
    for athlete in athletes:
        name = f"- {athlete.fname} {athlete.lname}"
        if top_margin < 1 * inch:  # Check if we need a new page
            p.showPage()
            top_margin = height - 1 * inch
        p.drawString(col_positions[1], top_margin, name)
        top_margin -= line_height
    
    
        # Divider line
    top_margin -= line_height * 1.5
    # p.line(left_margin, top_margin, width - left_margin, top_margin)/
    p.line(left_margin, top_margin, width - left_margin, top_margin)
    top_margin -= line_height
    
    # Table Row 2: Processing Fee
    if top_margin < 1 * inch:
        p.showPage()
        top_margin = height - 0.5 * inch
    
    p.drawString(col_positions[0], top_margin, "Processing Fee")
    p.drawString(col_positions[1], top_margin, "Transaction processing fee")
    p.drawString(col_positions[2], top_margin, "1")
    p.drawString(col_positions[3], top_margin, f"UGX {flat_fee:,.2f}")
    p.drawString(col_positions[4], top_margin, f"UGX {flat_fee:,.2f}")
    top_margin -= line_height * 2
    
    # Payment Summary
    p.setFont("Helvetica", 10)
    p.drawRightString(width - left_margin - 2*inch, top_margin, "Subtotal:")
    p.drawRightString(width - left_margin, top_margin, f"UGX {subtotal:,.2f}")
    top_margin -= line_height
    

    
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB( 0.0, 0.0, 0.502)  # Dark gray for date
    p.drawRightString(width - left_margin - 2*inch, top_margin, "Total:")
    p.drawRightString(width - left_margin, top_margin, f"UGX {total:,.2f}")
    top_margin -= line_height * 3
    
    
    
    
        # Reset to black for subsequent text
    p.setFillColorRGB(0, 0, 0)
    # Footer
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(1.0, 0.0, 0.0)  # Dark blue color for title
    p.drawString(left_margin, top_margin, "Thanks for your business!")
    top_margin -= line_height * 2
    
    # Powered by (optional)
    p.setFont("Helvetica", 8)
    p.drawString(left_margin, top_margin, "POWERED BY")
    p.setFont("Helvetica-Bold", 8)
    p.drawString(left_margin + 0.9 * inch, top_margin, "USSSA FINANCE SYSTEM")
    
    # Finish
    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_id}.pdf"'
    return response


