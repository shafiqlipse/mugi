from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from .views import *

from .views import *


urlpatterns = [
    # venues
    path("export_ecsv/", export_ecsv, name="export_ecsv"),
    path("team_accred/<int:id>", Accreditation, name="team_accred"),
    path("team_occred/<int:id>", Occreditation, name="team_occred"),
    path("team_album/<int:id>", Albums, name="team_album"),
    path("team_cert/<int:id>", Certificate, name="team_cert"),
    path("team_cort/<int:id>", Cortificate, name="team_cort"),
    path("school_enrollments/", SchoolEnrollments, name="school_enrollments"),
    path("all_enrollments/", AllEnrollments, name="all_enrollments"),
    path(
        "school_enrollment/<int:id>",
        school_enrollment_details,
        name="school_enrollment",
    ),
    path(
        "delete_school_enrollment/<int:id>",
        school_enroll_delete,
        name="delete_school_enrollment",
    ),
    path(
        "update_school_enrollment/<int:id>",
        school_enrollment_update,
        name="update_school_enrollment",
    ),
    path(
        "remove-athlete/<int:enrollment_id>/<int:athlete_id>/",
        remove_athlete,
        name="remove_athlete",
    ),
    # path("process-payment/", process_payment, name="process_payment"),  # Add this line
    path("prepare-cert/<int:id>/", prepare_certificate, name="prepare_cert"),
    path("prepare-accred/<int:id>/", prepare_accreditation, name="prepare_accred"),
    path('get-sports/', get_sports, name='get_sports'),
    # Add more URLs as ne
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
