from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from school.views import *


urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("school-dashboard/", Dash, name="schooldash"),
    path("alltransfers/", AllTransfers, name="alltransfers"),
    path("championships/", championships, name="championships"),
    path("sport/", sports, name="sports"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
