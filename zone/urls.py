from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from debug_toolbar.toolbar import debug_toolbar_urls
from .views import *


urlpatterns = [
    path("zonalchair/", zonalchair_list, name="zonalchair_list"),
    path("zonalchair/create/", zonalchair_create, name="zonalchair_create"),
    path("zonalchair/<int:pk>/", zonalchair_detail, name="zonalchair_detail"),
    path("zonalchair/<int:pk>/update/", zonalchair_update, name="zonalchair_update"),
    path("zonalchair/<int:pk>/delete/", zonalchair_delete, name="zonalchair_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()
