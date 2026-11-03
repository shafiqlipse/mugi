from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib import messages
from accounts.decorators import *
from .models import Athlete
from payments.services import *
import requests
from django.conf import settings
from django.db import transaction
import random
import logging
# Create your views here.
ATHLETE_EDIT_FEE = 50000

logger = logging.getLogger("airtel")


def athletes_to_edit(request):
    school = request.user.school
    
    athletes = Athlete.objects.filter(school=school).exclude(status = "COMPLETED")
    
    context = {"athletes":athletes}
    return render(request, "athletes/athletes_to_edit.html", context)

@login_required
@login_required
def request_athlete_edit(request, id):
    school = request.user.school
    athlete = get_object_or_404(Athlete, id=id, school=school)

    # one open request per athlete
    open_req = AthleteEditRequest.objects.filter(athlete=athlete, status__in=AthleteEditRequest.OPEN_STATUSES).first()
    if open_req:
        messages.warning(request, "This athlete already has an open edit request.")
        return redirect('edit_request_detail', request_id=open_req.id)

    form = AthleteEditRequestForm(request.POST or None, request.FILES or None, athlete=athlete)
    
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            edit_request = form.save(commit=False)
            edit_request.requested_by = request.user
            edit_request.save()

        def link(payment):
            edit_request.payment = payment
            edit_request.save(update_fields=['payment'])

        payment, success, _ = create_and_initiate_payment(
            payment_type='EDIT',
            amount=ATHLETE_EDIT_FEE,
            phone_number=form.cleaned_data['phone_number'],
            related_obj_setter=link,
        )
        if success:
            messages.success(request, f"Request submitted. Approve the UGX {payment.amount:,.0f} prompt on your phone.")
        else:
            messages.error(request, "Request saved, but the payment prompt could not be sent. You can retry from the request page.")
        return redirect('edit_request_detail', request_id=edit_request.id)

    return render(request, 'athletes/request_edit.html', {'form': form, 'athlete': athlete})


@login_required
def edit_rejected_request(request, request_id):
    edit_request = get_object_or_404(
        AthleteEditRequest, id=request_id, status='REJECTED', school=request.user.school
    )
    form = AthleteEditRequestForm(
        request.POST or None, request.FILES or None,
        athlete=edit_request.athlete, instance=edit_request,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()  # resubmit() runs inside; no new payment
        messages.success(request, "Request resubmitted for review.")
        return redirect('edit_request_detail', request_id=edit_request.id)
    return render(request, 'athletes/request_edit.html', {'form': form, 'athlete': edit_request.athlete})


#@user_passes_test(is_secretariat)  # swap for your real permission check
def review_edit_request(request, request_id):
    edit_request = get_object_or_404(
        AthleteEditRequest.objects.select_related('athlete', 'school', 'payment'),
        id=request_id, status='PENDING_REVIEW',
    )
    diff = [
        {'field': f, 'old': edit_request.original_data.get(f), 'new': new}
        for f, new in edit_request.requested_changes.items()
    ]

    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('admin_comment', '').strip()
        if action == 'approve':
            try:
                edit_request.approve(request.user)
                messages.success(request, "Changes applied to the athlete record.")
                return redirect('edit_request_queue')
            except ValidationError as e:
                messages.error(request, e.message)
        elif action == 'reject':
            if not comment:
                messages.error(request, "A comment is required when rejecting.")
            else:
                edit_request.reject(request.user, comment)
                messages.success(request, "Request rejected.")
                return redirect('edit_request_queue')

    return render(request, 'athletes/review_edit_request.html', {'edit_request': edit_request, 'diff': diff})

def edit_request_success(request):
    return render(request, 'athletes/edit_request_success.html')

def edit_requests_list(request):
    requests = AthleteEditRequest.objects.select_related('athlete', 'requested_by', 'school').filter(status = 'COMPLETED')
    return render(request, 'athletes/edit_requests_list.html', {'requests': requests})


def my_edit_requests_list(request):
    school = request.user.school
    requests = AthleteEditRequest.objects.select_related('athlete', 'requested_by', 'school').filter(school=school)
    return render(request, 'athletes/edit_requests_list.html', {'requests': requests})

def delete_athlete_edit(request, id):
    stud = AthleteEditRequest.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("my_edit_requests_list")

    return render(request, "athletes/delete_ath.html", {"obj": stud})



def done_edit_requests_list(request):
    requests = AthleteEditRequest.objects.select_related('athlete', 'requested_by', 'school').filter(status='Approved')
    return render(request, 'athletes/edit_requests_list.html', {'requests': requests})

@login_required
def edit_request_detail(request, request_id):
    reviewer = request.user  # swap for your real permission check

    qs = AthleteEditRequest.objects.select_related('athlete', 'school', 'payment')
    if not reviewer:
        qs = qs.filter(school=request.user.school)  # schools only see their own
    edit_request = get_object_or_404(qs, id=request_id)

    if request.method == 'POST':
        if not reviewer:
            return HttpResponseForbidden()

        if edit_request.status != 'COMPLETED':
            messages.error(request, "This request is not awaiting review.")
            return redirect('edit_request_detail', request_id=edit_request.id)

        action = request.POST.get('action')
        comment = request.POST.get('admin_comment', '').strip()

        if action == 'approve':
            try:
                edit_request.approve(request.user)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return redirect('edit_request_detail', request_id=edit_request.id)
            messages.success(request, "Edit request approved and changes applied.")
            return redirect('edit_requests_list')

        elif action == 'reject':
            if not comment:
                messages.error(request, "Please give a reason for rejecting this request.")
                return redirect('edit_request_detail', request_id=edit_request.id)
            edit_request.reject(request.user, comment)
            messages.info(request, "Edit request rejected.")
            return redirect('edit_requests_list')

    return render(request, 'athletes/edit_request_detail.html', {
        'edit_request': edit_request,
        'diff': edit_request.get_diff(),
        'is_reviewer': reviewer,
        'can_review': reviewer and edit_request.status == 'COMPLETED',
    })