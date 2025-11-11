from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import *

from .views import *


urlpatterns = [
    # venues
    path("addtrainee/", trainee_add, name="addtrainee"),
    # path("addtrainee/", trainee_add, name="addtrainee"),
    path("ittf_trainee_add/", ittf_trainee_add, name="ittf_trainee_add"),
    # path("teccred/", teccreditation, name="teccred"),
    path('export_tcsv/', export_tcsv, name='export_tcsv'),
    path("trainees/", trainees, name="trainees"),
    path("archived-trainees/", archived_trainees, name="archived_trainees"),
    path("unpaid-trainees/", unpaid_trainees, name="unpaid_trainees"),
    path('get-courses/', get_courses, name='get_courses'),
    path('get-venues/', get_venues, name='get_venues'),
    path('get-level/', get_levels, name='get_levels'),
    path("trainee/<int:id>", trainee_details, name="trainee"),
    path("delete_trainee/<int:id>", trainee_delete, name="delete_trainee"),
    path("update_trainee/<int:id>", trainee_update, name="update_trainee"),
    path("activate_trainee/<int:id>", activate_trainee, name="activate_trainee"),
    path("payment_success/", payment_success, name="payment_success"),  # Add this line
    path("ittfpayment_success/", ittfpayment_success, name="ittfpayment_success"),  # Add this line
    path("ittf_trainees/", ittf_trainees, name="ittf_trainees"),  # Add this line
    
    # path('airtel/payment/callback/', airtel_payment_callback, name='airtel_payment_callback'),
    # Add more URLs as needed
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
