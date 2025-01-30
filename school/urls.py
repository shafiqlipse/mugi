from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [
    path("addschool/", school_new, name="newschool"),
    path("school/<int:id>", school_detail, name="schooldetail"),
    path("updateschool/<int:id>", schoolupdate, name="schoolupdate"),
    path("delschool/<int:id>", DeleteSchool, name="delschool"),
    path("schools/", Schools, name="schools"),
    # path("schools/", Schools, name="schools"),
    # path("updateofficial/<int:id>", OfficialDetail, name="updateofficial"),
    path("official/<int:id>", OfficialDetail, name="official"),
    path("export_csv/", export_csv, name="export_csv"),
    path("export_pdf/", exportp_csv, name="export_pdf"),
    # path("export_pdf/", exportp_csv, name="export_pdf"),
    path("newathlete/", newAthlete, name="add_athlete"),
    path("athletes/", athletes, name="athletes"),
    path("archives/", archives, name="archives"),
    path("allathletes/", all_athletes, name="allathletes"),
    path("athlete/<int:id>", AthleteDetail, name="athlete"),
    path("editathlete/<int:id>", AthleteUpdate, name="updateathlete"),
    path("delete-athlete/<int:id>", DeleteAthlete, name="del_athlete"),
    path("screens/", Screened, name="screened"),
    # path("export_pdf/", exportp_csv, name="export_pdf"),
    path('export-scsv/', export_scsv, name='export_scsv'),
    path('pay/<int:id>/', initiate_payment, name='payment'),
    path('registration/', payment_view, name='registration'),
    # path("export_pdf/", exportp_csv, name="export_pdf"),
    path("newofficial/", Official, name="add_official"),
    path("officials/", school_offs, name="officials"),
    path("allofficials/", all_officials, name="allofficials"),
    path("official/<int:id>", OfficialDetail, name="official"),
    path("delete-official/<int:id>", DeleteOfficial, name="del_official"),
    # path("delete-official/<int:id>", DeleteOfficial, name="del_official"),
    # path("delete-official/<int:id>", DeleteOfficial, name="del_official"),
    # path("delete-official/<int:id>", DeleteOfficial, name="del_official"),
    path('airtel/payment/callback/', airtel_payment_callback, name='airtel_payment_callback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
