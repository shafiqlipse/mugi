from urllib import response
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
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
from django.db.models import Q, Exists, OuterRef
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from payments.services import create_and_initiate_payment
from django.views.decorators.http import require_POST






logger = logging.getLogger("airtel")


TRANSFER_AMOUNT = 10000  # move to settings if this varies or changes over time

@login_required
@require_POST
def initiate_transfer(request, id):
    school = request.user.school
    athlete = get_object_or_404(Athlete, id=id)

    if athlete.school == school:
        messages.error(request, "Athlete already belongs to your school.")
        return redirect("mytransfers")

    form = InitiateTransferForm(request.POST, request.FILES, athlete=athlete)
    if not form.is_valid():
        for field_errors in form.errors.values():
            messages.error(request, field_errors[0])
        return redirect("mytransfers")

    phone_number = form.cleaned_data["phone_number"]
    documents = form.cleaned_data.get("documents")

    def link_transfer(payment):
        transfer_request = TransferRequest.objects.create(
            requester=school,
            athlete=athlete,
            owner=athlete.school,
            status="pending",
            requested_at=timezone.now(),
        )
        if documents:
            transfer_request.documents = documents
            transfer_request.save(update_fields=["documents"])
        TransferPayment.objects.create(transfer=transfer_request, payment=payment)

    try:
        payment, success, response = create_and_initiate_payment(
            payment_type="TRANSFER",
            amount=TRANSFER_AMOUNT,
            phone_number=phone_number,
            related_obj_setter=link_transfer,
        )
    except IntegrityError:
        messages.warning(request, "You already have a pending transfer request for this athlete.")
        return redirect("mytransfers")
    except ValidationError as e:
        messages.error(request, "; ".join(e.messages))
        return redirect("mytransfers")

    if not success:
        messages.error(request, "Payment could not be initiated. Please try again.")
        return redirect("mytransfers")

    messages.success(request, f"Payment request sent to {phone_number}. Enter your Airtel PIN to complete.")
    return redirect("mytransfers")

@login_required(login_url="login")
def accept_transfer(request, id):
    transfer_request = get_object_or_404(TransferRequest, id=id)

    if transfer_request.owner != request.user.school:
        return JsonResponse({
            "status": "error",
            "message": "You are not authorized to accept this transfer."
        }, status=403)

    if not transfer_request.requires_acceptance:
        return JsonResponse({
            "status": "error",
            "message": "This athlete does not require owning-school acceptance."
        }, status=400)

    if transfer_request.status != "paid":
        return JsonResponse({
            "status": "error",
            "message": "This transfer request is no longer awaiting acceptance."
        }, status=400)

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

    form = AcceptTransferForm(request.POST, request.FILES, instance=transfer_request)
    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "message": form.errors.get("documents", ["Invalid file."])[0]
        }, status=400)

    try:
        with transaction.atomic():
            # Reject all other paid transfers for the same athlete
            TransferRequest.objects.filter(
                athlete=transfer_request.athlete, status="paid"
            ).exclude(id=transfer_request.id).update(
                status="rejected", rejected_at=timezone.now()
            )
            transfer_request = form.save(commit=False)
            transfer_request.accept_transfer()
    except ValueError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    except Exception:
        logger.exception("Error accepting transfer %s", id)
        return JsonResponse({"status": "error", "message": "An error occurred while processing your request."}, status=500)

    return JsonResponse({
        "status": "success",
        "message": "Transfer request accepted successfully. Other pending transfers for this athlete have been rejected."
    })


@login_required(login_url="login")
def approve_transfer(request, id):
    transfer_request = get_object_or_404(TransferRequest, id=id)

    if not getattr(request.user, "is_tech", False):
        messages.error(request, "You must be a technical user to approve transfers.")
        return redirect("alltransfers")

    try:
        transfer_request.approve_transfer(approver=request.user)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("alltransfers")
    except Exception:
        logger.exception("Error approving transfer %s", id)
        messages.error(request, "An error occurred while approving the transfer.")
        return redirect("alltransfers")

    messages.success(
        request,
        f"Transfer approved successfully. {transfer_request.athlete} has been transferred to {transfer_request.requester}",
    )
    return redirect("alltransfers")


@login_required(login_url="login")
def cancel_transfer(request, id):
    transfer_request = get_object_or_404(TransferRequest, id=id)

    if request.user.school != transfer_request.requester:
        messages.error(request, "You are not authorized to cancel this transfer request.")
        return redirect("mytransfers")

    if transfer_request.status != "pending":
        messages.error(request, "You can only cancel transfer requests that haven't been paid for yet.")
        return redirect("mytransfers")

    transfer_request.delete()
    messages.success(request, "Transfer request cancelled successfully.")
    return redirect("mytransfers")


@login_required(login_url="login")
def reject_transfer(request, id):
    """Admin rejects a paid or accepted transfer, with an explanatory message."""
    transfer_request = get_object_or_404(TransferRequest, id=id)

    if not getattr(request.user, "is_tech", False):
        messages.error(request, "You must be a technical user to reject transfers.")
        return redirect("alltransfers")

    if request.method == "POST":
        form = TransferRejectionForm(request.POST)
        if form.is_valid():
            try:
                transfer_request.reject_transfer()
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("alltransfers")

            transfer_request.documents = None
            transfer_request.save(update_fields=["documents"])

            rejection_message = form.cleaned_data["message"]
            transfer_message = TransferMessage.objects.create(
                transfer=transfer_request,
                sender=request.user,
                message=rejection_message,
            )
            transfer_message.recipients.add(request.user.school)

            notification = Notification.objects.create(
                sender=request.user,
                verb=f"Transfer request for {transfer_request.athlete} was rejected.",
                target=f"Athlete ID: {transfer_request.athlete.id}",
                created_at=timezone.now(),
            )
            notification.recipients.add(transfer_request.owner, transfer_request.requester)

            messages.success(request, "Transfer request rejected, and message sent.")
            return redirect("alltransfers")
    else:
        form = TransferRejectionForm()

    return render(request, "transfers/transfer.html", {"form": form, "transfer": transfer_request})


@login_required(login_url="login")
def reject_request(request, id):
    """Owning school declines to release an active athlete before it reaches acceptance."""
    transfer_request = get_object_or_404(TransferRequest, id=id)

    if transfer_request.owner != request.user.school:
        messages.error(request, "You are not authorized to reject this transfer request.")
        return redirect("myrequests")

    if not transfer_request.requires_acceptance:
        messages.error(request, "This transfer does not require your school's response.")
        return redirect("myrequests")

    try:
        transfer_request.reject_transfer()
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("myrequests")

    messages.success(request, "Transfer request rejected successfully.")
    return redirect("myrequests")

@login_required(login_url="login")
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


@login_required(login_url="login")
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


@login_required(login_url="login")
def transfers(request):
    user = request.user
    school = user.school

    current_year = timezone.now().year

    approved_transfer_exists = TransferRequest.objects.filter(
        athlete=OuterRef("pk"),
        status="approved",
        requested_at__year=current_year
    )

    athletes_list = (
        Athlete.objects.select_related("school")
        .exclude(
            Q(school=school) | Q(status="COMPLETED")
        )
        .annotate(has_approved_transfer=Exists(approved_transfer_exists))
        .filter(has_approved_transfer=False)
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



# @transfer_required
@login_required
def AllTransfers(request):
    transfers = TransferRequest.objects.filter(status ='Accepted')
    
    context = {"transfers": transfers}
    return render(request, "all/transfers.html", context)

# @transfer_required
@login_required
def Pending_Transfers(request):
    transfers = TransferRequest.objects.filter(status ='paid')
    
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)

@login_required
def Approved_Transfers(request):
    transfers = TransferRequest.objects.filter(status ='Approved')
    
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)


@login_required
def Archieved_Transfers(request):
    transfers = TransferRequest.objects.filter(is_archived = True)
    
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)