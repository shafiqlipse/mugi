from django.shortcuts import render, redirect, get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from io import BytesIO
from .models import *
from .forms import *
from django.db import IntegrityError
from django.core.files.base import ContentFile
import base64
from django.contrib.auth.decorators import login_required
from .filters import TraineeFilter 
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import random
from django.db import transaction
from django.db import transaction as db_transaction
from django.conf import settings
import requests
import re
from school.views import get_airtel_token
from django.urls import reverse
from django.http import JsonResponse
logger = logging.getLogger(__name__)

airtel_logger = logging.getLogger('airtel_callback')  # Use the specific logger

def get_venues(request):
    season_id = request.GET.get("season_id")  # Get the selected season ID from the request
    if season_id:
        try:
            season = Season.objects.get(id=season_id)  # Retrieve the season instance
            venues = season.venue_set.values(
                "id", "name"
            )  # Get related venues
            return JsonResponse(list(venues), safe=False)
        except Season.DoesNotExist:
            return JsonResponse({"error": "Season not found"}, status=404)
    return JsonResponse([], safe=False)

def get_courses(request):
    venue_id = request.GET.get("venue_id")  # Get the selected venue ID from the request
    if venue_id:
        try:
            venue = Venue.objects.get(id=venue_id)  # Retrieve the venue instance
            courses = venue.courses.values("id", "name")
  # Get related courses
            return JsonResponse(list(courses), safe=False)
        except Venue.DoesNotExist:
            return JsonResponse({"error": "COurse not found"}, status=404)
    return JsonResponse([], safe=False)

def get_levels(request):
    course_id = request.GET.get("course_id")

    if not course_id:
        return JsonResponse({"error": "Missing course_id parameter"}, status=400)

    try:
        course = Course.objects.select_related("level").get(id=course_id)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)

    if course.level:
        level_data = {
            "id": course.level.id,
            "name": course.level.name,
        }
        return JsonResponse(level_data)
    else:
        return JsonResponse({"message": "This course has no level assigned"})

def get_level(request):
    course_id = request.GET.get("course_id")  # Get the selected course ID from the request
    if course_id:
        try:
            courses = Course.objects.get(id=course_id)  # Retrieve the course instance
            levels = courses.level_set.values(
                "id", "name"
            )  # Get related disciplines
            return JsonResponse(list(levels), safe=False)
        except Venue.DoesNotExist:
            return JsonResponse({"error": "Level not found"}, status=404)
    return JsonResponse([], safe=False)



def generate_unique_transaction_id():
    """Generate a unique 12-digit transaction ID."""
    while True:
        transaction_id = str(random.randint(10**11, 10**12 - 1))  # 12-digit random number
        if not Trainee.objects.filter(transaction_id=transaction_id).exists():  # Ensure uniqueness
            return transaction_id


import time

def generate_transaction_id():
    """
    Generates a globally unique 12-digit numeric ID.
    Format:
    7 digits timestamp + 5 digits random
    """
    timestamp_part = int(time.time() * 1000) % 10_000_000  # last 7 digits of ms timestamp
    random_part = random.randint(10_000, 99_999)           # 5 random digits

    return f"{timestamp_part:07d}{random_part}"



def trainee_add(request):
    if request.method == 'POST':
        form = TraineesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                phone_number = form.cleaned_data.get('phone_number')

                if not phone_number:
                    messages.error(request, "Phone number is required.")
                    return render(request, 'trainees/add_trainee.html', {'form': form})

                # 💰 Payment details
                amount = 60500  # Total amount (UGX 110,000 + 500 fee)

                # 🎯 Save trainee record first (pending payment)
                with transaction.atomic():
                    trainee = form.save(commit=False)
                    trainee.amount = amount
                    trainee.payment_status = "Pending"
                    trainee.transaction_id = generate_unique_transaction_id()
                    trainee.save()

                # 🔐 Get Airtel token
                token = get_airtel_token()
                if not token:
                    messages.error(request, "Failed to connect to Airtel. Try again later.")
                    return render(request, 'trainees/add_trainee.html', {'form': form})

                # 🌍 Airtel API setup
                payment_url = "https://openapi.airtel.ug/merchant/v2/payments/"
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
                    "reference": str(trainee.transaction_id),
                    "subscriber": {
                        "country": "UG",
                        "currency": "UGX",
                        "msisdn": msisdn,
                    },
                    "transaction": {
                        "amount": float(amount),
                        "country": "UG",
                        "currency": "UGX",
                        "id": trainee.transaction_id,
                    },
                }

                # 🚀 Send payment request
                response = requests.post(payment_url, json=payload, headers=headers)
                logger.info(f"Airtel Payment Response ({response.status_code}): {response.text}")

                # 🧾 Handle response
                if response.status_code == 200:
                    messages.success(
                        request,
                        f"Payment initiated successfully! Please confirm UGX {amount} on your Airtel line."
                    )
                    return redirect('payment_success')
                else:
                    trainee.payment_status = "Failed"
                    trainee.save()
                    messages.error(request, "Payment initiation failed. Please try again.")
                    return render(request, 'trainees/add_trainee.html', {'form': form})

            except Exception as e:
                logger.error(f"❌ Error during trainee payment: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred while processing your payment.")
                return render(request, 'trainees/add_trainee.html', {'form': form})

    else:
        form = TraineesForm()

    # Default GET request
    return render(request, 'trainees/add_trainee.html', {'form': form, 'amount': '60,500'})
 

def ittf_trainee_add(request):
    if request.method == 'POST':
        form = ITTFTraineesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                phone_number = form.cleaned_data.get('phone_number')

                if not phone_number:
                    messages.error(request, "Phone number is required.")
                    return render(request, 'trainees/add_trainee.html', {'form': form})

                # 💰 Payment details
                amount = 10500  # Total amount (UGX 110,000 + 500 fee)

                # 🎯 Save trainee record first (pending payment)
                with transaction.atomic():
                    ittftrainee = form.save(commit=False)
                    ittftrainee.amount = amount
                    ittftrainee.payment_status = "Pending"
                    ittftrainee.transaction_id = generate_unique_itransaction_id()
                    ittftrainee.save()

                # 🔐 Get Airtel token
                token = get_airtel_token()
                if not token:
                    messages.error(request, "Failed to connect to Airtel. Try again later.")
                    return render(request, 'trainees/add_trainee.html', {'form': form})

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
                    "reference": str(ittftrainee.transaction_id),
                    "subscriber": {
                        "country": "UG",
                        "currency": "UGX",
                        "msisdn": msisdn,
                    },
                    "transaction": {
                        "amount": float(amount),
                        "country": "UG",
                        "currency": "UGX",
                        "id": ittftrainee.transaction_id,
                    },
                }

                # 🚀 Send payment request
                response = requests.post(payment_url, json=payload, headers=headers)
                logger.info(f"Airtel Payment Response ({response.status_code}): {response.text}")

                # 🧾 Handle response
                if response.status_code == 200:
                    messages.success(
                        request,
                        f"Payment initiated successfully! Please confirm UGX {amount} on your Airtel line."
                    )
                    return redirect('payment_success')
                else:
                    ittftrainee.payment_status = "Failed"
                    ittftrainee.save()
                    messages.error(request, "Payment initiation failed. Please try again.")
                    return render(request, 'ittf/add_trainee.html', {'form': form})

            except Exception as e:
                logger.error(f"❌ Error during trainee payment: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred while processing your payment.")
                return render(request, 'ittf/add_trainee.html', {'form': form})

    else:
        form = ITTFTraineesForm()

    # Default GET request
    return render(request, 'ittf/add_trainee.html', {'form': form, 'amount': '10,500'})
 
    
def payment_success(request):
    return render(request, 'trainees/successpage.html', {
        
    })
    

 # Assume you have created this filter

    
def ittfpayment_success(request):
    

    return render(request, 'ittf/successpage.html', {
        
    })
    

 # Assume you have created this filter


@login_required(login_url="login")
def trainees(request):
    # Get all trainees
    trainees = Trainee.objects.all().order_by("-created_at")
    completed_transactions = trainees.filter(payment_status="Completed")
    total_collected = completed_transactions.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0

    # Apply the filter
    trainee_filter = TraineeFilter(request.GET, queryset=trainees)
    alltrainees = trainee_filter.qs

    if request.method == "POST":
        # Check which form was submitted
        if "Accreditation" in request.POST:
            template = get_template("reports/acrred.html")
            filename = "Trainee_Accreditation.pdf"
        elif "Certificate" in request.POST:
            template = get_template(
                "reports/certficate_temaplate.html"
            )  # Your certificate template
            filename = "Trainee_Certificate.pdf"
        else:
            return HttpResponse("Invalid form submission")

        # Generate PDF
        context = {"alltrainees": alltrainees}
        html = template.render(context)

        # Create a PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")

        pdf_buffer.seek(0)

        # Return the PDF as a response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf_buffer.getvalue())
        return response
    else:
        # Render the filter form
        return render(
            request,
            "trainees/trainees.html",
            {"trainee_filter": trainee_filter,"total_collected":total_collected},
        )


 # Assume you have created this filter


@login_required(login_url="login")
def ittf_trainees(request):
    # Get all trainees
    trainees = ITTFTrainee.objects.all().order_by("-created_at")
    completed_transactions = trainees.filter(payment_status="Completed")
    total_collected = completed_transactions.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
    

    # Apply the filter


    if request.method == "POST":
        # Check which form was submitted
        if "Accreditation" in request.POST:
            template = get_template("ittf/reports/acrred.html")
            filename = "Trainee_Accreditation.pdf"
        elif "Certificate" in request.POST:
            template = get_template(
                "ittf/reports/certficate_temaplate.html"
            )  # Your certificate template
            filename = "Trainee_Certificate.pdf"
        else:
            return HttpResponse("Invalid form submission")

        # Generate PDF
        context = {"trainees": trainees}
        html = template.render(context)

        # Create a PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")

        pdf_buffer.seek(0)

        # Return the PDF as a response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf_buffer.getvalue())
        return response
    else:
        # Render the filter form
        return render(
            request,
            "ittf/trainees.html",
            {"trainees": trainees, "total_collected": total_collected},
        )


def ittf_trainee_details(request, id):
    trainee = ITTFTrainee.objects.get(id=id)

    context = {"trainee": trainee}
    return render(request, "ittf/trainee.html", context)

def trainee_details(request, id):
    trainee = Trainee.objects.get(id=id)

    context = {"trainee": trainee}
    return render(request, "trainees/trainee.html", context)


def trainee_update(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":
        form = TraineesForm(request.POST, request.FILES, instance=trainee)
        if form.is_valid():
            try:
                new_trainee = form.save(commit=False)


                new_trainee.save()
                messages.success(
                    request,
                    "Updated successfully! ",
                )
                return redirect("trainees")

            except IntegrityError:
                messages.error(request, "There was an error saving the trainee.")
                return render(request, "trainee_new.html", {"form": form})

    else:
        form = TraineesForm(instance=trainee)

    context = {
        "form": form,
        "trainee": trainee,
    }
    return render(request, "trainees/update_trainee.html", context)


def trainee_delete(request, id):
    stud = Trainee.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("trainees")

    return render(request, "trainees/delete_trainee.html", {"obj": stud})



def itrainee_update(request, id):
    trainee = get_object_or_404(ITTFTrainee, id=id)

    if request.method == "POST":
        form = ITTFTraineesForm(request.POST, request.FILES, instance=trainee)
        if form.is_valid():
            try:
                new_trainee = form.save(commit=False)

                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        new_trainee.photo = data  # Assign cropped image
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "ittf/add_trainee.html", {"form": form})

                new_trainee.save()
                messages.success(
                    request,
                    "Updated successfully! ",
                )
                return redirect("ittf_trainees")

            except IntegrityError:
                messages.error(request, "There was an error saving the trainee.")
                return render(request, "ittf/add_trainee.html", {"form": form})

    else:
        form = TraineesForm(instance=trainee)

    context = {
        "form": form,
        "trainee": trainee,
    }
    return render(request, "update_trainee.html", context)


def itrainee_delete(request, id):
    stud = ITTFTrainee.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("ittf_trainees")
    return render(request, "trainees/delete_trainee.html", {"obj": stud})


import csv
from django.http import HttpResponse


def export_tcsv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'

    # Create a CSV writer object using the HttpResponse as the file.
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "id",
            "first_name",
            "last_name",
            "place",
            "contract",
            "district",
            "venue",
            "course",
            "level",
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in Trainee.objects.all():
        writer.writerow(
            [
                obj.id,
                obj.first_name,
                obj.last_name,
                obj.place,
                obj.contact,
                obj.district,
                obj.venue,
                obj.course,
                obj.level,
            ]
        )  # Replace with your model's fields

    return response


def export_itcsv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'

    # Create a CSV writer object using the HttpResponse as the file.
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "id",
            "first_name",
            "last_name",
            "school",
            "contract",
            "district",

        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in ITTFTrainee.objects.filter(payment_status="Completed"):
        writer.writerow(
            [
                obj.id,
                obj.first_name,
                obj.last_name,
                obj.school,
                obj.contact,
                obj.district,
 
            ]
        )  # Replace with your model's fields

    return response


def activate_trainee(request, id):
    trainee = get_object_or_404(Trainee, id=id)
    trainee.payment_status = "Completed"
    trainee.save()
    messages.success(request, "Trainee activated successfully.")
    return redirect("trainees") 


def activate_itrainee(request, id):
    trainee = get_object_or_404(ITTFTrainee, id=id)
    trainee.payment_status = "Completed"
    trainee.save()
    messages.success(request, "Trainee activated successfully.")
    return redirect("ittf_trainees") 


def archived_trainees(request):
    archived_trainees = Trainee.objects.filter(venue__status="Inactive").order_by("-created_at")
    trainee_filter = TraineeFilter(request.GET, queryset=archived_trainees)
    archived_trainees = trainee_filter.qs

    return render(
        request,
        "trainees/archived_trainees.html",
        {"trainee_filter": trainee_filter, "archived_trainees": archived_trainees},
    )

def unpaid_trainees(request):
    unpaid_trainees = Trainee.objects.filter(venue__status="Active",payment_status="Pending").order_by("-created_at")
    trainee_filter = TraineeFilter(request.GET, queryset=unpaid_trainees)
    unpaid_trainees = trainee_filter.qs

    return render(
        request,
        "trainees/archived_trainees.html",
        {"trainee_filter": trainee_filter, "unpaid_trainees": unpaid_trainees},
    )