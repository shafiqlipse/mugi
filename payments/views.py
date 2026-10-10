from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
# ---------------Accounts-----------------
from .models import *
from .filters import *
from django.db.models import Sum, Count, F

@login_required
def accounts(request):
    
    total_earnings = Payment.objects.filter(status="COMPLETED").aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending = Payment.objects.filter(status="PENDING").count()
    total_completed = Payment.objects.filter(status="COMPLETED").count()
    total_schools = Payment.objects.values('school').distinct().count()
    total_athletes = Payment.objects.values('athletes').distinct().count()

    recent_transactions = Payment.objects.order_by('-created_at')[:10]  # Last 10 transactions
    

    
    context = {
        'total_earnings': total_earnings,
        'total_pending': total_pending,
        'total_completed': total_completed,
        'total_schools': total_schools,
        'total_athletes': total_athletes,
        'recent_transactions': recent_transactions,
        # 'recent_transactions': recent_transactions,
    }
    return render(request, "dashboard/accounts.html", context)

@login_required
def allpayments(request):
    payments = Payment.objects.filter(status="COMPLETED").order_by('-created_at')    
    
    # Apply filtering
    payments_filter = PaymentFilter(request.GET, queryset=payments)
    filtered_payments = payments_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_payments, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_payments = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": paginated_payments,
        "payment_filter": payments_filter,
    }
   
    return render(request, "payments.html", context)

@login_required
def pending_payments(request):
    pawyments = Payment.objects.filter(status="PENDING").order_by('-created_at')  
    payments_filter = PaymentFilter(request.GET, queryset=pawyments)
    filtered_payments = payments_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_payments, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_payments = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": paginated_payments,
        "payment_filter": payments_filter,
    }
    # Pass the filter to the context for rendering the filter form
 

    return render(request, "pending.html", context)

@login_required
def activate_payment(request, id):
    payment = get_object_or_404(Payment,id=id)
    payment.status = "COMPLETED"
    payment.save() # Save the updated status
    messages.success(request, f"Payment {payment} is now {payment.status}.")
    return redirect("pending_payments")
#     context = {"payment": payment}


@login_required
def payment_detail(request, id):
    payment = get_object_or_404(Payment,id=id)
    builder = RECEIPT_CONTEXT_BUILDERS.get(payment.payment_type)
    if not builder:
        raise Http404("Transaction detail not available for this payment type")

    context = {'payment': payment}
    context.update(builder(payment)) 
    return render(request, "payment_detail.html", context)
   
#     context = {"payment": payment}


@login_required
def transactions(request):
    school = request.user.school
    payments = Payment.objects.filter(
        status="COMPLETED",
        # payment_type="REGISTRATION",
        # registration_payment__school=school,
    ).order_by('-created_at')

    context = {"payments": payments}
    # Pass the filter to the context for rendering the filter form
 

    return render(request, "complete.html", context)

   
def payment_success(request, transaction_id):
    payment = Payment.objects.filter(transaction_id=transaction_id).first()
    
    if not payment:
        return render(request, 'payment_failed.html', {'error': 'Transaction not found'})

    return render(request, 'payments/payment_success.html', {
        'amount': payment.amount,
        'transaction_id': payment.transaction_id,
        'timestamp': payment.created_at,  # Make sure your Payment model has `created_at`
    })
 
 
 # payments/views.py


from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
import io
from .models import Payment
from .receipts import RECEIPT_CONTEXT_BUILDERS

def generate_receipt(request, transaction_id):
    payment = get_object_or_404(Payment, transaction_id=transaction_id, status='COMPLETED')

    builder = RECEIPT_CONTEXT_BUILDERS.get(payment.payment_type)
    if not builder:
        raise Http404("Receipt not available for this payment type")

    context = {'payment': payment, 'logo_path': 'https://reg.usssaonline.com/static/lib/images/logo-receipt-01.png'}
    context.update(builder(payment))

    html = render_to_string('receipt_pdf.html', context)
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        return HttpResponse("PDF generation error", status=500)

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_id}.pdf"'
    return response



import json
import logging

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from payments.models import Payment
from school.models import RegistrationPayment
from transfers.models import TransferPayment
from editrequests.models import AthleteEditRequest
from training.models import Trainee

airtel_logger = logging.getLogger("airtel")


@csrf_exempt
def airtel_payment_callback(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    try:
        raw_body = request.body.decode("utf-8")
        airtel_logger.info("Airtel callback received: %s", raw_body)
        payload = json.loads(raw_body)

        txn = payload.get("transaction", {})
        transaction_id = txn.get("id")
        status_code = txn.get("status_code")
        airtel_money_id = txn.get("airtel_money_id")

        if not transaction_id:
            airtel_logger.warning("Callback without transaction id")
            return JsonResponse({"error": "Missing transaction id"}, status=400)

        # TS success, TF failed, TE expired, TA ambiguous, TIP in progress
        status_mapping = {
            "TS": "COMPLETED",
            "TF": "FAILED",
            "TE": "FAILED",
            "TA": "PENDING",
            "TIP": "PENDING",
        }
        new_status = status_mapping.get(status_code)
        if new_status is None:
            airtel_logger.warning(
                "Unknown status_code %r for %s, treating as PENDING",
                status_code, transaction_id,
            )
            new_status = "PENDING"

        with transaction.atomic():
            # -------------------------------------------------
            # 1. Payment (single source of truth, row locked)
            # -------------------------------------------------
            payment = (
                Payment.objects.select_for_update()
                .filter(transaction_id=transaction_id)
                .first()
            )
            if not payment:
                airtel_logger.warning("No payment for transaction %s", transaction_id)
                return JsonResponse({"message": "Callback processed"}, status=200)

            # Airtel may retry: a completed payment is final, same status = no-op
            if payment.status == "COMPLETED" or payment.status == new_status:
                return JsonResponse({"message": "Callback processed"}, status=200)

            payment.status = new_status
            if new_status == "COMPLETED":
                payment.paid_at = timezone.now()
            payment.save()

            # -------------------------------------------------
            # 2. Sync the model this payment belongs to
            # -------------------------------------------------
            if payment.payment_type == "REGISTRATION":
                registration_payment = RegistrationPayment.objects.filter(payment=payment).first()
                if registration_payment and new_status == "COMPLETED":
                    registration_payment.athletes.update(status="ACTIVE")
                # FAILED / PENDING: athletes stay inactive
                
                
            elif payment.payment_type == "TRANSFER":
                if new_status == "COMPLETED":
                    for transfer_payment in payment.transfer_payments.select_related("transfer"):
                        transfer = transfer_payment.transfer
                        transfer.status = "paid"
                        transfer.save()                
                
            elif payment.payment_type == "TRAINING":
                trainee = Trainee.objects.filter(payment=payment).first()
                if trainee and new_status == "COMPLETED":
                    trainee.status = "Active"
                    trainee.save()

            elif payment.payment_type == "EDIT":
                edit_request = AthleteEditRequest.objects.filter(payment=payment).first()
                if edit_request and edit_request.status in ("PENDING", "FAILED", "AWAITING PAYMENT"):
                    edit_request.status = {
                        "COMPLETED": "PENDING REVIEW",  # paid -> secretariat queue
                        "FAILED": "FAILED",
                        "PENDING": "PENDING",
                    }[new_status]
                    edit_request.save()

            elif payment.payment_type == "TRAINING":
                # Nothing to update: Trainee reads trainee.payment.status
                pass

            else:
                airtel_logger.warning(
                    "Payment %s has unhandled payment_type %s",
                    payment.pk, payment.payment_type,
                )

        airtel_logger.info(
            "Processed callback: transaction=%s, status=%s", transaction_id, new_status
        )
        return JsonResponse({"message": "Callback processed"}, status=200)

    except json.JSONDecodeError:
        airtel_logger.error("Callback with invalid JSON")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        airtel_logger.exception("Callback error")
        return JsonResponse({"error": "Internal Error"}, status=500)