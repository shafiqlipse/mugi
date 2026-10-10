from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [
    path("addschool/", school_new, name="newschool"),
    path("school/<int:id>", school_detail, name="schooldetail"),
    path("updateschool/<int:id>", school_update, name="school_update"),
    path("delschool/<int:id>", DeleteSchool, name="delschool"),
    path("schools/", Schools, name="schools"),
    path('schools/data/', school_data_view, name='school_data'),
    # path('schools/data/', school_data_view, name='school_data'),
    # path('schools/data/', school_data_view, name='school_data'),
    
    path("newathlete/", newAthlete, name="add_athlete"),
    path("athletes/", athletes, name="athletes"),
    path("dathletes/", red_athletes, name="dathletes"),
    path("archives/", archives, name="archives"),
    path("allathletes/", all_athletes, name="allathletes"),
    path("athlete/<int:id>", AthleteDetail, name="athlete"),
    path("editathlete/<int:id>", AthleteUpdate, name="updateathlete"),
    path("delete-athlete/<int:id>", DeleteAthlete, name="del_athlete"),
    path('athletes/data/', athlete_data_view, name='athlete_data'),
    path('archives/data/', archives_data_view, name='archives_data'),
    # path('archives/data/', archives_data_view, name='archives_data'),
    
    path("screens/", Screened, name="screened"),
    # path('archives/data/', archives_data_view, name='archives_data'),
    path("newofficial/", Official, name="add_official"),
    path("officials/", school_offs, name="officials"),
    path('officials/update/<int:id>/', update_official, name='update_official'),
    path("official/<int:id>", OfficialDetail, name="official"),
    path("delete-official/<int:id>", DeleteOfficial, name="del_official"),
    path("activate_official/<int:id>", activate_official, name="activate_official"),
    path("deactivate_official/<int:id>", deactivate_official, name="deactivate_official"),
    # path("deactivate_official/<int:id>", deactivate_official, name="deactivate_official"),
    # path('archives/data/', archives_data_view, name='archives_data'),
    path('pay/<int:id>/', payment_view, name='payment'),
    path('registration/', payment_view, name='registration'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
