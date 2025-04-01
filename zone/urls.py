from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from debug_toolbar.toolbar import debug_toolbar_urls
from .views import *


urlpatterns = [
    path("zonalchair/", zonalchair_list, name="zonalchair_list"),
    path("dashboard/chair/", zonalchair_dashboard, name="zonalchair_dashboard"),
    path("zonalchair/<int:id>/", activate_zonalchair, name="zonalchair_activate"),
    path("zonalchair/schools/", zonalchair_schools, name="zonalchair_schools"),
    path("zonalchair/athletes/", zonalchair_athletes, name="zonalchair_athletes"),
    path("zonalchair/officials/", zonalchair_officials, name="zonalchair_officials"),
    path("zonalchair/enrollments/", zonalchair_enrollments, name="zonalchair_enrollments"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()
