from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import *

from .views import *


urlpatterns = [
    # venues
    path("addtrainee/", redirection, name="addtrainee"),
    # path("teccred/", teccreditation, name="teccred"),
    path('export-csv/', export_csv, name='export_csv'),
    path("trainees/", trainees, name="trainees"),
    path('get-disciplines/', get_disciplines, name='get_disciplines'),
    path('get-venues/', get_venues, name='get_venues'),
    path("trainee/<int:id>", trainee_details, name="trainee"),
    path("delete_trainee/<int:id>", trainee_delete, name="delete_trainee"),
    path("update_trainee/<int:id>", trainee_update, name="update_trainee"),
    path("activate_trainee/<int:id>", activate_trainee, name="activate_trainee"),
    # path("process-payment/", process_payment, name="process_payment"),  # Add this line
    # Add more URLs as ne
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
