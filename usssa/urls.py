from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.urls import path
from dashboard.views import *
from accounts.views import *
from base.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    # venues
    path("", home, name="home"),
    # venues
    path("dashboard/", include("dashboard.urls")),
    path("auth/", include("accounts.urls")),
    path("school/", include("school.urls")),
    path("enrollment/", include("enrollment.urls")),
    # path("transfers/", include("transfers.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
