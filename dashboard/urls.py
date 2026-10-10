from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from accounts.views import *
from school.views import *


urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("school_dashboard/", school_dashboard, name="school_dashboard"),
    # path('user/edit/<int:id>/', edit_user, name='edit_user'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
