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
# from accounts.decorators import transfer_required


# @transfer_required
# Assume you create a form for transfer request


def transfers(request):
    user = request.user
    school = user.school
    athletes_list = Athlete.objects.all().exclude(school=school)
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

def initiate_transfer(request, id):
    try:
        user = request.user
        school = user.school  # The requesting school
        athlete = get_object_or_404(Athlete, id=id)

        # Prevent transfer request if athlete is already in requested school
        if athlete.school == school:
            messages.error(
                request, "Cannot request transfer for athlete already in your school."
            )
            return redirect("athletes_list")

        # Check if there's already a pending transfer request from the same school
        existing_request_from_same_school = TransferRequest.objects.filter(
            athlete=athlete, requester=school, status="pending"
        ).exists()

        if existing_request_from_same_school:
            messages.error(
                request, "Your school has already initiated a transfer request for this athlete."
            )
            return redirect("mytransfers")

        # Create the transfer request
        transfer_request = TransferRequest.objects.create(
            requester=school,
            athlete=athlete,
            owner=athlete.school,
            status="pending",
            requested_at=timezone.now(),
        )

        messages.success(request, "Transfer request initiated successfully.")
        return redirect("mytransfers")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("transfers")
def myTransfers(request):
    user = request.user
    school = user.school
    mytransfers = TransferRequest.objects.filter(requester=school)
    context = {"mytransfers": mytransfers}
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



def myRequests(request):
    user = request.user
    school = user.school
    mytransfers = TransferRequest.objects.filter(owner=school, status="pending")
    context = {"mytransfers": mytransfers}
    return render(request, "transfers/my_requests.html", context)


from django.http import JsonResponse
from django.template.loader import render_to_string

from django.db.models import Q

def accept_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Ensure only the owning school can accept the transfer
        if transfer_request.owner != request.user.school:
            return JsonResponse({
                "status": "error",
                "message": "You are not authorized to accept this transfer."
            })

        if transfer_request.status != "pending":
            return JsonResponse({
                "status": "error",
                "message": "This transfer request is no longer pending."
            })

        if request.method == "POST":
            form = AcceptTransferForm(request.POST, request.FILES, instance=transfer_request)
            if form.is_valid():
                # Reject all other pending transfers for the same athlete
                TransferRequest.objects.filter(
                    Q(athlete=transfer_request.athlete) & Q(status="pending")
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
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Validate if user is authorized to reject transfers
        if not getattr(request.user, "is_tech", False):
            messages.error(request, "You must be a technical user to reject transfers.")
            return redirect("alltransfers")

        # Check if transfer is in accepted or pending state
        if transfer_request.status not in ["accepted", "pending"]:
            messages.error(request, "Only pending or accepted transfers can be rejected.")
            return redirect("alltransfers")

        # Update status to pending and clear documents
        transfer_request.status = "pending"
        transfer_request.documents = None
        transfer_request.save()

        # Create a notification
        notification = Notification.objects.create(
            sender=request.user,
            verb=f"Transfer request for {transfer_request.athlete} was rejected.",
            target=f"Athlete ID: {transfer_request.athlete.id}",
            created_at=now(),
        )
        # Add recipients (e.g., owning and requesting schools)
        notification.recipients.add(transfer_request.owner, transfer_request.requester)

        messages.success(
            request, f"Transfer request for {transfer_request.athlete} has been rejected and reset to pending."
        )
        return redirect("alltransfers")

    except Exception as e:
        messages.error(request, f"An error occurred while rejecting the transfer: {str(e)}")
        return redirect("alltransfers")


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

