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
    path('export-dcsv/', export_csv, name='export_dcsv'),
    path("delegates/", delegates, name="delegates"),
    path("delegate/<int:id>", delegate_details, name="delegate"),
    path("delete_delegate/<int:id>", delegate_delete, name="delete_delegate"),
    path("update_delegate/<int:id>", delegate_update, name="update_delegate"),
    # path("process-payment/", process_payment, name="process_payment"),  # Add this line
    # Add more URLs as ne
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
