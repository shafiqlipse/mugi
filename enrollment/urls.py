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
    path("achive_enrollments/", AchivesEnrollments, name="achive_enrollments"),
    path("active_enrollments/", ActiveEnrollments, name="active_enrollments"),
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
    # Add more URLs as ne
    path("athletics_enrollments/", athleticsEnrollments, name="athletics_enrollments"),
    path("athletics_enrollments/<int:id>/", athletics_enrollment_details, name="athletics_enrollment"),
    # path("athletics_enrollments/<int:id>/", athletics_enrollment_details, name="athletics_enrollment"),
    path("athletics_accred/<int:id>", AAcreditation, name="athletics_accred"),
    path("athletics_cert/<int:id>", Aertificate, name="athletics_occred"),
    path("athletics_enroll_delete/<int:id>", athletics_enroll_delete, name="athletics_enroll_delete"),
    path("athletics_album/<int:id>", AAlbums, name="athletics_album"),
        path(
        "remove_athletics/<int:enrollment_id>/<int:athlete_id>/",
        remove_athletics,
        name="remove_athletics",
    ),
    # Add more URLs as ne
    path("U14athletics_enrollments/", uthleticsEnrollments, name="U14athletics_enrollments"),
    path("U14athletics_enrollments/<int:id>/", Uthletics_enrollment_details, name="U14athletics_enrollment"),
    # path("athletics_enrollments/<int:id>/", athletics_enrollment_details, name="athletics_enrollment"),
    path("U14athletics_accred/<int:id>", UAcreditation, name="U14athletics_accred"),
    path("U14athletics_cert/<int:id>", Uertificate, name="U14athletics_occred"),
    path("U14athletics_enroll_delete/<int:id>", Uthletics_enroll_delete, name="U14athletics_enroll_delete"),
    path("U14athletics_album/<int:id>", UAlbums, name="U14athletics_album"),
        path(
        "remove_athletics/<int:enrollment_id>/<int:athlete_id>/",
        remove_athletics,
        name="remove_athletics",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
