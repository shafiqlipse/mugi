from django.shortcuts import render, redirect, get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from io import BytesIO
from .models import *
from .forms import *
from django.db import IntegrityError
import base64
from django.contrib.auth.decorators import login_required
from .filters import TraineeFilter 
import logging
from django.conf import settings
import requests
import re
from school.views import get_airtel_token
from django.http import JsonResponse

airtel_logger = logging.getLogger('airtel_callback')  # Use the specific airtel_logger

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


import logging
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from payments.models import Payment
from payments.services import initiate_airtel_payment, generate_transaction_id # placeholder: your service layer

airtel_logger = logging.getLogger("airtel")


def _venue_amounts():
    return {
        str(v.id): {
            "residential": float(v.residential_amount or 0),
            "non_residential": float(v.non_residential_amount or 0),
        }
        for v in Venue.objects.filter(status="Active")
    }


def trainee_add(request):
    amount = 0
    ctx = lambda form: {"form": form, "amount": amount, "venue_amounts": _venue_amounts()}

    if request.method != "POST":
        return render(request, "trainees/add_trainee.html", ctx(TraineesForm()))

    form = TraineesForm(request.POST, request.FILES)
    
    print("PHONE:", request.POST.get("phone_number"), "| ERRORS:", form.errors.as_json())
    
    if not form.is_valid():
        venue_id = form.data.get("venue")
        residence_type = form.data.get("residence_type")
        if venue_id and residence_type:
            venue = Venue.objects.filter(pk=venue_id).first()
            if venue:
                amount = (venue.residential_amount if residence_type == "Residential"
                          else venue.non_residential_amount) or 0
        return render(request, "trainees/add_trainee.html", ctx(form))

    phone_number = form.cleaned_data["phone_number"]  # form-only field, not on the model

    try:
        with transaction.atomic():
            trainee = form.save(commit=False)
            trainee.season = trainee.venue.season

            amount = trainee.calculate_amount()
            if not amount:
                form.add_error("venue", "No fee is configured for this venue and residence type.")
                return render(request, "trainees/add_trainee.html", ctx(form))

            payment = Payment.objects.create(
                 payment_type='TRAINING',
                amount=amount,
                phone_number=phone_number,
                status="Pending",
                transaction_id=generate_transaction_id(),
                # purpose/payment_type="trainee", if your Payment model has one
            )
            trainee.payment = payment
            trainee.save()
    except Exception:
        airtel_logger.exception("Error creating trainee/payment")
        messages.error(request, "An error occurred while processing your registration.")
        return render(request, "trainees/add_trainee.html", ctx(form))

    # The external call happens AFTER the transaction commits, never inside it
    try:
        ok = initiate_airtel_payment(payment)  # builds payload, calls Airtel, logs response
    except Exception:
        airtel_logger.exception("Airtel initiation error for payment %s", payment.pk)
        ok = False

    if ok:
        messages.success(
            request,
            f"Payment initiated. Please confirm UGX {payment.amount:,.0f} on your Airtel line.",
        )
        return redirect("payment_success")

    payment.status = "Failed"
    payment.save(update_fields=["status"])
    messages.error(request, "Payment initiation failed. Please try again.")
    return render(request, "trainees/add_trainee.html", ctx(form))


    
def payment_success(request):
    return render(request, 'trainees/successpage.html', {
        
    })
    

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



def activate_trainee(request, id):
    trainee = get_object_or_404(Trainee, id=id)
    trainee.payment_status = "Completed"
    trainee.save()
    messages.success(request, "Trainee activated successfully.")
    return redirect("trainees") 



def archived_trainees(request):
    archived_trainees = Trainee.objects.filter(venue__status="Inactive").order_by("-created_at")
    trainee_filter = TraineeFilter(request.GET, queryset=archived_trainees)
    archived_trainees = trainee_filter.qs

    return render(
        request,
        "trainees/archived_trainees.html",
        {"trainee_filter": trainee_filter, "archived_trainees": archived_trainees},
    )

