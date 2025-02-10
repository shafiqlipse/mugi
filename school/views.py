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
    officials_count = school_official.objects.filter(school=school).count
    athletes_bcount = Athlete.objects.filter(school=school,gender="male").count
    athletes_gcount = Athlete.objects.filter(school=school,gender="female").count
    officials_bcount = school_official.objects.filter(school=school,gender="M").count
    officials_gcount = school_official.objects.filter(school=school,gender="F").count
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

        return redirect(reverse('schooldetail', args=[id]))
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

def payment_view(request):
    school = request.user.school  # Get the logged-in user's school

    if request.method == 'POST':
        form = PaymentForm(request.POST, school=school)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            selected_athletes = form.cleaned_data['athletes']
            total_amount = selected_athletes.count() * 3000  # UGX 20,000 per athlete

            # Generate a unique transaction_id upfront
            transaction_id = str(uuid.uuid4()).replace("-", "")[:12]  

            # Create a Payment record with transaction_id
            payment = Payment.objects.create(
                school=school,
                amount=total_amount,
                phone_number=phone_number,
                status="PENDING",
                transaction_id=transaction_id  # ✅ Assign transaction_id here
            )
            payment.athletes.set(selected_athletes)
            # Redirect to initiate payment
            return redirect('payment', payment.id)

    else:
        form = PaymentForm(school=school)

    return render(request, 'emails/payment_form.html', {'form': form})
import json
import uuid
import requests
from django.conf import settings
from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def get_airtel_token():
    """
    Retrieve Airtel Money OAuth token.
    """
    try:
        url = "https://openapiuat.airtel.africa/auth/oauth2/token"
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

        payment_url = "https://openapiuat.airtel.africa/merchant/v2/payments/"
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
            "reference": str(payment.id),  # Use the Payment ID as the reference
            "subscriber": {
                "country": "UG",
                "currency": "UGX",
                "msisdn": re.sub(r"\D", "", str(payment.phone_number)),  # Remove non-numeric characters
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

        if response.status_code == 200:
            # Update the Payment record with the transaction ID
            payment.id = transaction_id
            payment.status = "PENDING"  # Set initial status
            payment.save()
            return JsonResponse({"message": "Payment initiated successfully", "response": response.json()})
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


# def airtel_payment_callback(request):
#     try:
#         data = json.loads(request.body)
#         logger.info(f"Received Airtel callback: {data}")

#         # Extract transaction details
#         transaction = data.get("transaction", {})
#         transaction_id = transaction.get("id")  # Ensure this matches what was sent
#         status_code = transaction.get("status_code")  # Airtel success code
#         airtel_money_id = transaction.get("airtel_money_id")  # Airtel money transaction ID

#         # Check if transaction_id exists in our database
#         payment = Payment.objects.filter(transaction_id=transaction_id).first()

#         if not payment:
#             logger.error(f"No payment found for transaction_id: {transaction_id}")
#             return JsonResponse({"error": "Invalid transaction ID"}, status=400)

#         # Only update if it's still pending
#         if payment.status == "PENDING":
#             if status_code == "TS":  # Airtel's success status code
#                 payment.status = "COMPLETED"
#                 payment.save()
#                 logger.info(f"Payment {payment.id} completed successfully.")
#                 return JsonResponse({"message": "Payment completed successfully"})
#             else:
#                 logger.warning(f"Payment {payment.id} failed with status {status_code}")
#                 return JsonResponse({"error": "Payment not successful"}, status=400)

#         return JsonResponse({"message": "Payment already processed"})

#     except json.JSONDecodeError:
#         logger.error("Invalid JSON received in callback")
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     except Exception as e:
#         logger.error(f"Error processing payment callback: {str(e)}")
#         return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
def airtel_payment_callback(request):

    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    try:
        # Log the raw request body
        raw_body = request.body.decode('utf-8')
        logger.info(f"Raw Request Body: {raw_body}")

        # Parse JSON payload
        payload = json.loads(raw_body)
        logger.info(f"Parsed JSON Payload: {json.dumps(payload, indent=2)}")

        # Extract transaction details (corrected)
        transaction = payload.get("transaction", {})  # Ensure transaction exists
        transaction_id = transaction.get("id")  # Airtel's transaction ID
        status_code = transaction.get("status_code")  # Example: "TS" (Success)
        airtel_money_id = transaction.get("airtel_money_id")  # Airtel reference ID

        logger.info(f"Transaction ID: {transaction_id}, Status Code: {status_code}, Airtel Money ID: {airtel_money_id}")

        # Ensure required fields exist
        if not all([transaction_id, status_code, airtel_money_id]):
            logger.error("❌ Missing required fields in callback payload")
            return JsonResponse({"error": "Invalid callback payload"}, status=400)

        # Process the payment callback (Update Payment record)
        return JsonResponse({"message": "Callback processed successfully"}, status=200)

    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON payload received")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        logger.error(f"❌ Error processing callback: {str(e)}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)