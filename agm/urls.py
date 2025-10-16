from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import *

from .views import *


urlpatterns = [
    # venues
    path("adddelegate/", delegate_add, name="adddelegate"),
    # path("teccred/", teccreditation, name="teccred"),
    path('export-dcsv/', export_dcsv, name='export_dcsv'),
    path("delegates/", delegates, name="delegates"),
    path("delegate/<int:id>", delegate_details, name="delegate"),
    path("delete_delegate/<int:id>", delegate_delete, name="delete_delegate"),
    path("update_delegate/<int:id>", delegate_update, name="update_delegate"),
    # path("process-
    # 
    # venues
    path("addcomiser/", comiser_add, name="addcomiser"),
    path("teccred/", generate_accreditation_pdf, name="teaccred"),
    # path('export-dcsv/', export_csv, name='export_dcsv'),
    path("comisers/", comisers, name="comisers"),
    path("comiser/<int:id>", comiser_details, name="comiser"),
    path("delete_comiser/<int:id>", comiser_delete, name="delete_comiser"),
    path("update_comiser/<int:id>", comiser_update, name="update_comiser"),
    # path("process-p
    # payment/", process_payment, name="process_payment"),  # Add this line
    # Add more URLs as ne
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
