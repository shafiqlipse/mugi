from urllib import response
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from school.views import get_airtel_token
from .models import TransferRequest
from school.models import *
from dashboard.models import *
from .forms import *
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from school.filters import AthleteFilter
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator
import requests
from django.conf import settings
from django.http import JsonResponse
import logging
from django.urls import reverse
from .filters import TransferPaymentFilter
import random
from django.db import transaction

logger = logging.getLogger("airtel")
# from accounts.decorators import transfer_required
import time

def generate_ttransaction_id():
    """
    Generates a globally unique 12-digit numeric ID.
    Format:
    7 digits timestamp + 5 digits random
    """
    timestamp_part = int(time.time() * 1000) % 10_000_000  # last 7 digits of ms timestamp
    random_part = random.randint(10_000, 99_999)           # 5 random digits

    return f"{timestamp_part:07d}{random_part}"



# @transfer_required
# Assume you create a form for transfer request


def transfers(request):
    user = request.user
    school = user.school
    athletes_list = Athlete.objects.select_related("school").exclude(
    Q(school=school) | Q(status="COMPLETED")
).order_by("id")
    athlete_filter = AthleteFilter(request.GET, queryset=athletes_list)
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
    return render(request, "transfers/initiate_transfer.html", context)


import re

def format_msisdn(phone):
    digits = re.sub(r"\D", "", str(phone))

    if digits.startswith("256"):
        return digits
    if digits.startswith("0"):
        return digits[1:]
    return digits
# # @require_POST


def initiate_transfer(request, id):
    try:
        user = request.user

        # 🔴 Prevent anonymous access crash
        if not user.is_authenticated:
            messages.error(request, "Please login first.")
            return redirect("login")

        school = user.school
        athlete = get_object_or_404(Athlete, id=id)
        phone_number = request.POST.get("phone_number")

        if not phone_number:
            messages.error(request, "You must provide a valid Airtel number.")
            return redirect("athletes_list")

        # Prevent same-school transfer
        if athlete.school == school:
            messages.error(request, "Athlete already belongs to your school.")
            return redirect("athletes_list")

        # Prevent duplicate pending requests
        if TransferRequest.objects.filter(
            athlete=athlete,
            requester=school,
            status="pending"
        ).exists():
            messages.warning(request, "You already have a pending transfer request.")
            return redirect("mytransfers")

        # ===============================
        # STEP 1: Get fresh Airtel token
        # ===============================
        token = get_airtel_token()
        if not token:
            messages.error(request, "Payment service unavailable. Try later.")
            return redirect("mytransfers")

        # ===============================
        # STEP 2: Prepare payment request
        # ===============================
        payment_url = "https://openapi.airtel.ug/merchant/v2/payments/"
        transaction_id = generate_unique_ttransaction_id()
        amount = 10000

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Country": "UG",
            "X-Currency": "UGX",
            "Authorization": f"Bearer {token}",
            "x-signature": settings.AIRTEL_API_SIGNATURE,
            "x-key": settings.AIRTEL_API_KEY,
            "Connection": "close",  # critical
        }

        payload = {
            "reference": str(transaction_id),
            "subscriber": {
                "country": "UG",
                "currency": "UGX",
                "msisdn": format_msisdn(phone_number),
            },
            "transaction": {
                "amount": str(amount),
                "country": "UG",
                "currency": "UGX",
                "id": transaction_id,
            }
        }

        # ===============================
        # STEP 3: Call Airtel API (OUTSIDE DB TRANSACTION)
        # ===============================
        try:
            with requests.Session() as session:
                session.headers.update(headers)
                response = session.post(
                    payment_url,
                    json=payload,
                    timeout=(5, 30)
                )

            logger.info(f"Airtel Response: {response.status_code} {response.text}")

        except Exception as e:
            logger.error(f"Airtel request failed: {str(e)}")
            messages.error(request, "Payment request failed. Try again.")
            return redirect("mytransfers")

        if response.status_code != 200:
            messages.error(request, "Payment could not be initiated.")
            return redirect("mytransfers")

        # ===============================
        # STEP 4: Save DB records safely
        # ===============================
        with transaction.atomic():

            transfer_request = TransferRequest.objects.create(
                requester=school,
                athlete=athlete,
                owner=athlete.school,
                status="pending",
                requested_at=timezone.now(),
            )

            TransferPayment.objects.create(
                transfer=transfer_request,
                amount=amount,
                phone_number=phone_number,
                status="PENDING",
                transaction_id=transaction_id,
                paid_at=timezone.now(),
            )

        # ===============================
        # STEP 5: Correct user message
        # ===============================
        messages.success(
            request,
            f"Payment request sent to {phone_number}. "
            "Enter your Airtel PIN to complete."
        )

        return redirect("mytransfers")

    except Exception as e:
        logger.error(f"Transfer error: {str(e)}")
        messages.error(request, "Unexpected error occurred.")
        return redirect("mytransfers")
# def initiate_transfer(request, id):
#     try:
#         user = request.user
#         school = user.school
#         athlete = get_object_or_404(Athlete, id=id)
#         phone_number = request.POST.get("phone_number")

#         # ✅ Require a phone number before proceeding
#         if not phone_number:
#             messages.error(request, "You must provide a valid Airtel number to pay for this transfer.")
#             return redirect("athletes_list")

#         # ✅ Prevent same-school requests
#         if athlete.school == school:
#             messages.error(request, "You cannot request a transfer for an athlete already in your school.")
#             return redirect("athletes_list")

#         # ✅ Prevent duplicate pending requests
#         if TransferRequest.objects.filter(athlete=athlete, requester=school, status="pending").exists():
#             messages.warning(request, "You already have a pending transfer request for this athlete.")
#             return redirect("mytransfers")

#         # ✅ Everything inside one atomic transaction
#         with transaction.atomic():
#             # Step 1: Get Airtel token
#             token = get_airtel_token()
#             if not token:
#                 messages.error(request, "Failed to authenticate with Airtel. Please try again later.")
#                 return redirect("mytransfers")

#             # Step 2: Prepare the Airtel payment request
#             payment_url = "https://openapi.airtel.africa/merchant/v2/payments/"
#             transaction_id = generate_unique_ttransaction_id()  
#             amount = 10000  # Transfer fee amount


#             headers = {
#                 "Accept": "*/*",
#                 "Content-Type": "application/json",
#                 "X-Country": "UG",
#                 "X-Currency": "UGX",
#                 "Authorization": f"Bearer {token}",
#                 "x-signature": settings.AIRTEL_API_SIGNATURE,
#                 "x-key": settings.AIRTEL_API_KEY,
#             }

#             payload = {
#                 "reference": str(transaction_id),
#                 "subscriber": {
#                     "country": "UG",
#                     "currency": "UGX",
#                     "msisdn": re.sub(r"\D", "", str(phone_number)).lstrip('0'),
#                 },
#                 "transaction": {
#                     "amount": float(amount),
#                     "country": "UG",
#                     "currency": "UGX",
#                     "id": transaction_id,
#                 }
#             }

#             headers["Connection"] = "close"  # prevent stale pooled connections

#             with requests.Session() as session:
#                 session.headers.update(headers)
#                 response = session.post(payment_url, json=payload, timeout=(5,30))

#             logger.info(f"Payment Response: {response.status_code}, {response.text}")


#             # Step 3: Check payment result
#             if response.status_code != 200:
#                 messages.error(request, "Payment could not be initiated. Please check your Airtel number or try again later.")
#                 # rollback automatically since atomic()
#                 return redirect("mytransfers")

#             # Step 4: Create TransferRequest only after successful payment initiation
#             transfer_request = TransferRequest.objects.create(
#                 requester=school,
#                 athlete=athlete,
#                 owner=athlete.school,
#                 status="pending",  # mark as pending after success
#                 requested_at=timezone.now(),
#             )

#             # Step 5: Record payment info
#             TransferPayment.objects.create(
#                 transfer=transfer_request,
#                 amount=amount,
#                 phone_number=phone_number,
#                 status="PENDING",
#                 transaction_id=transaction_id,
#                 paid_at=timezone.now(),
#             )

#             messages.success(request, f"Payment request  of {amount} sent to your phone! Transfer request for {athlete.fname} {athlete.lname} has been submitted.")
#             return redirect("mytransfers")

#     except Exception as e:
#         logger.error(f"Transfer payment error: {str(e)}")
#         messages.error(request, f"An unexpected error occurred: {str(e)}")
#         return redirect("mytransfers")



def myTransfers(request):
    user = request.user
    school = user.school
    mytransfers = TransferRequest.objects.select_related("owner").filter(requester=school)

    trans_messages = TransferMessage.objects.filter(
        transfer__requester=school
    ) | TransferMessage.objects.filter(
        transfer__owner=school
    )
    context = {"mytransfers": mytransfers, "trans_messages": trans_messages}
    return render(request, "transfers/my_transfers.html", context)



# @transfer_required
def transfer_details(request, id):
    transfer = get_object_or_404(TransferRequest, id=id)

    # Check if user is a technical user
    if not getattr(request.user, "is_tech", False):
        messages.error(request, "You must be a technical user to view this transfer.")
        return redirect("alltransfers")

    context = {
        "transfer": transfer,
    }

    return render(request, "transfers/transfer.html", context)


@login_required(login_url="login")
def myRequests(request):
    user = request.user
    school = user.school
    mytransfers = TransferRequest.objects.select_related("owner").filter(owner=school, status="paid")
    context = {"mytransfers": mytransfers}
    return render(request, "transfers/my_requests.html", context)




def accept_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Ensure only the owning school can accept the transfer
        if transfer_request.owner != request.user.school:
            return JsonResponse({
                "status": "error",
                "message": "You are not authorized to accept this transfer."
            })

        if transfer_request.status != "paid":
            return JsonResponse({
                "status": "error",
                "message": "This transfer request is no longer pending."
            })

        if request.method == "POST":
            form = AcceptTransferForm(request.POST, request.FILES, instance=transfer_request)
            if form.is_valid():
                # Reject all other pending transfers for the same athlete
                TransferRequest.objects.filter(
                    Q(athlete=transfer_request.athlete) & Q(status="paid")
                ).exclude(id=transfer_request.id).update(status="rejected")

                # Accept the current transfer
                transfer_request = form.save(commit=False)
                transfer_request.accept_transfer()  
                transfer_request.save()

                return JsonResponse({
                    "status": "success",
                    "message": "Transfer request accepted successfully. Other pending transfers for this athlete have been rejected."
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": form.errors.get('documents', ["Invalid file."])[0]
                })

        return JsonResponse({
            "status": "error",
            "message": "Invalid request method."
        })

    except Exception as e:
        print(f"Error in accept_transfer: {str(e)}")  # Debugging
        return JsonResponse({
            "status": "error",
            "message": "An error occurred while processing your request."
        })
        
        
@login_required
def approve_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Validate if user is a technical user
        if not getattr(request.user, "is_tech", False):
            messages.error(request, "You must be a technical user to approve transfers.")
            return redirect("alltransfers")

        # Check if transfer is in accepted state
        if transfer_request.status != "accepted":
            messages.error(request, "Only accepted transfers can be approved.")
            return redirect("alltransfers")

        # Check if documents were uploaded
        if not transfer_request.documents:
            messages.error(request, "Transfer cannot be approved without documents.")
            return redirect("alltransfers")

        # Approve the transfer
        transfer_request.approve_transfer(approver=request.user)
        messages.success(
            request,
            f"Transfer approved successfully. {transfer_request.athlete} has been transferred to {transfer_request.requester}",
        )

        return redirect("alltransfers")

    except Exception as e:
        messages.error(
            request, f"An error occurred while approving the transfer: {str(e)}"
        )
        return redirect("alltransfers")


def cancel_transfer(request, id):
    try:
        # Get the transfer request object
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Check if the requesting user has permission to cancel the transfer
        if request.user.school != transfer_request.requester:
            messages.error(request, "You are not authorized to cancel this transfer request.")
            return redirect("mytransfers")

        # Only allow pending transfer requests to be cancelled
        if transfer_request.status != "pending":
            messages.error(request, "You can only cancel pending transfer requests.")
            return redirect("mytransfers")

        # Delete the transfer request
        transfer_request.delete()
        messages.success(request, "Transfer request cancelled successfully.")
        return redirect("mytransfers")

    except Exception as e:
        messages.error(request, f"An error occurred while cancelling the transfer: {str(e)}")
        return redirect("mytransfers")
    
    

from django.utils.timezone import now
# from .models import Notification, TransferRequest

@login_required
def reject_transfer(request, id):
    transfer_request = get_object_or_404(TransferRequest, id=id)

    # Validate if user is authorized to reject transfers
    if not getattr(request.user, "is_tech", False):
        messages.error(request, "You must be a technical user to reject transfers.")
        return redirect("alltransfers")

    # Ensure the transfer is in an appropriate state
    if transfer_request.status not in ["accepted", "pending"]:
        messages.error(request, "Only pending or accepted transfers can be rejected.")
        return redirect("alltransfers")

    if request.method == "POST":
        form = TransferRejectionForm(request.POST)
        if form.is_valid():
            # Update the transfer request status
            transfer_request.status = "pending"
            transfer_request.documents = None  # Optional: Clear documents
            transfer_request.save()

            # Create a rejection message
            rejection_message = form.cleaned_data["message"]
            transfer_message = TransferMessage.objects.create(
                transfer=transfer_request,
                sender=request.user,
                message=rejection_message,
            )
            transfer_message.recipients.add(request.user.school)  # Ensure sender's school is notified

            # Create a notification for the rejection
            notification = Notification.objects.create(
                sender=request.user,
                verb=f"Transfer request for {transfer_request.athlete} was rejected.",
                target=f"Athlete ID: {transfer_request.athlete.id}",
                created_at=now(),
            )
            notification.recipients.add(transfer_request.owner, transfer_request.requester)

            messages.success(request, "Transfer request rejected, and message sent.")
            return redirect("alltransfers")

    else:
        form = TransferRejectionForm()

    return render(request, "transfers/transfer.html", {"form": form, "transfer": transfer_request})


def reject_request(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Validate if user is authorized to reject transfer requests
        if request.user.school != transfer_request.owner:
            messages.error(request, "You are not authorized to reject this transfer request.")
            return redirect("myrequests")

        # Only allow pending transfer requests to be rejected
        if transfer_request.status != "pending":
            messages.error(request, "You can only reject pending transfer requests.")
            return redirect("myrequests")

        # Change the status to 'rejected' instead of deleting the request
        transfer_request.status = "rejected"
        transfer_request.save()

        messages.success(request, "Transfer request rejected successfully.")
        return redirect("myrequests")

    except Exception as e:
        messages.error(request, f"An error occurred while rejecting the transfer request: {str(e)}")
        return redirect("myrequests")



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
            "athlete",
            "requesting school",
            "requesting school",
            "status",
            "requested at",
            "accepted at",
            "approved at",
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in TransferRequest.objects.all():
        writer.writerow(
            [
                obj.id,
                obj.athlete,
                obj.requester,
                obj.owner,
                obj.status,
                obj.requested_at,
                obj.accepted_at,
                obj.approved_at,
               
            ]
        )  # Replace with your model's fields

    return response

def transfer_payments(request):
    payments = TransferPayment.objects.select_related("transfer").all().order_by('id')  # Order by a unique field, like 'id'

    # Apply filtering
    payments_filter = TransferPaymentFilter(request.GET, queryset=payments)
    filtered_payments = payments_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_payments, 10)  # Show 10 payments per page
    page_number = request.GET.get("page")
    paginated_payments = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": paginated_payments,
        "payment_filter": payments_filter,
    }
    return render(request, "transfers/transfer_payments.html", context)



from django.utils import timezone

def archived_transfers(request):

    current_year = timezone.now().year

    archived_transfers = (
        TransferRequest.objects
        .filter(requested_at__year__lt=current_year)
        .order_by("-requested_at")
    )

    context = {"archived_transfers": archived_transfers}
    return render(request, "transfers/archived_transfers.html", context)




def activate_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Validate if user is a technical user
        if not getattr(request.user, "is_tech", False):
            messages.error(request, "You must be a technical user to activate transfers.")
            return redirect("alltransfers")

        # Check if transfer is in rejected state
        if transfer_request.status != "rejected":
            messages.error(request, "Only rejected transfers can be activated.")
            return redirect("alltransfers")

        # Activate the transfer
        transfer_request.status = "paid"
        transfer_request.save()
        messages.success(
            request,
            f"Transfer activated successfully. {transfer_request.athlete} transfer request is now pending.",
        )

        return redirect("alltransfers")

    except Exception as e:
        messages.error(
            request, f"An error occurred while activating the transfer: {str(e)}"
        )
        return redirect("alltransfers")