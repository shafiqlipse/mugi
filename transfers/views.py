from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import TransferRequest
from school.models import *
from .forms import *
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from school.filters import AthleteFilter
# from accounts.decorators import transfer_required


# @transfer_required
def approve_transfer(request, transfer_id):
    transfer_request = get_object_or_404(TransferRequest, id=transfer_id)

    # Check if the user has the right permissions (e.g., if they are the approver)
    if (
        request.user == transfer_request.approver
        and transfer_request.status == "accepted"
    ):
        transfer_request.approve_transfer()
        messages.success(
            request,
            "Transfer approved and athlete has been transferred to the new school.",
        )
    else:
        messages.error(
            request,
            "You are not authorized to approve this transfer or it is not ready for approval.",
        )

    return redirect("some_view_name")


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

        # Check if there's already a pending transfer request
        existing_request = TransferRequest.objects.filter(
            athlete=athlete, status="pending"
        ).exists()

        if existing_request:
            messages.error(
                request, "There is already a pending transfer request for this athlete."
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

    # Check if user has permission to view this transfer
    if not request.user.has_perm("transfers.approve_transfer"):
        messages.error(request, "You don't have permission to view this transfer.")
        return redirect("home")

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


def accept_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Ensure only the owning school can accept the transfer
        if transfer_request.owner != request.user.school:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "You are not authorized to accept this transfer.",
                }
            )

        if transfer_request.status != "pending":
            return JsonResponse(
                {
                    "status": "error",
                    "message": "This transfer request is no longer pending.",
                }
            )

        form = AcceptTransferForm(
            request.POST, request.FILES, instance=transfer_request
        )
        if form.is_valid():
            transfer_request = form.save(commit=False)
            transfer_request.accept_transfer()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Transfer request accepted successfully.",
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Please upload valid transfer documents.",
                }
            )

    except Exception as e:
        print(f"Error in accept_transfer: {str(e)}")  # For debugging
        return JsonResponse(
            {
                "status": "error",
                "message": "An error occurred while processing your request.",
            }
        )


@login_required
def approve_transfer(request, id):
    try:
        transfer_request = get_object_or_404(TransferRequest, id=id)

        # Validate if user has permission to approve transfers
        if not request.user.has_perm("transfers.approve_transfer"):
            messages.error(request, "You don't have permission to approve transfers.")
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
