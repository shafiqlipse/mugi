from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from dashboard.views import *
from accounts.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    # venues
    path("", user_login, name="login"),
    path("offline/", offline_view, name="offline"),
    # venues
    path("dashboard/", include("dashboard.urls")),
    path("auth/", include("accounts.urls")),
    path("enrollment/", include("enrollment.urls")),
    path("school/", include("school.urls")),
    path("payments/", include("payments.urls")),
    path("support/", include("support.urls")),
    path("transfers/", include("transfers.urls")),
    path("editrequests/", include("editrequests.urls")),
    path("training/", include("training.urls")),
    path("agm/", include("agm.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
