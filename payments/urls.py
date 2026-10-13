from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from school.views import *


urlpatterns = [

    # path("sport/", sports, name="sports"),
    path("accounts/", accounts, name="accounts"),
    path("payments/", allpayments, name="payments"),
    path("pending_payments/", pending_payments, name="pending_payments"),
    path("activate_payment/<int:id>", activate_payment, name="activate_payment"),
    path("payment_detail/<int:id>", payment_detail, name="payment_detail"),
    # path("delete_announcement/<int:id>", delete_announcement, name="delete_announcement"),
    path("transactions/", transactions, name="transactions"),
    # path("summery/", payment_summery, name="summery"),
    # path("athlete_summary/", athlete_summary, name="athlete_summary"),
    path("airtel/payment/callback/", airtel_payment_callback, name="airtel_payment_callback"),
    path('receipt/<str:transaction_id>/', generate_receipt, name='payment_receipt'),
    path('payment/success/<str:transaction_id>/', payment_success, name='payment_success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
