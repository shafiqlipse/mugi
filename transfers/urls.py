from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [
    path("initiate_transfer/<int:id>", initiate_transfer, name="initiate_transfer"),
    path("transfers/", transfers, name="transfers"),
    path("mytransfers/", myTransfers, name="mytransfers"),
    path("myrequests/", myRequests, name="myrequests"),
    path("accept/<int:id>/", accept_transfer, name="accept_transfer"),
    path("transfer_details/<int:id>", transfer_details, name="transfer_details"),
    path('transfers/approve/<int:id>/', approve_transfer, name='approve_transfer'),
    path("transfers/cancel/<int:id>/", cancel_transfer, name="cancel_transfer"),
    # path("updateofficial/<int:id>", OfficialDetail, name="updateofficial"),
    # path("export_pdf/", exportp_csv, name="export_pdf"),
    # path("export_pdf/", exportp_csv, name="export_pdf"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
