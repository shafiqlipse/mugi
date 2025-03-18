from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from dashboard.views import *
from accounts.views import *
from base.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    # venues
    path("", user_login, name="login"),
    # venues
    path("dashboard/", include("dashboard.urls")),
    path("auth/", include("accounts.urls")),
    path("school/", include("school.urls")),
    path("enrollment/", include("enrollment.urls")),
    path("transfers/", include("transfers.urls")),
    path("agm/", include("agm.urls")),
    path("zone/", include("zone.urls")),
    path("training/", include("training.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()
