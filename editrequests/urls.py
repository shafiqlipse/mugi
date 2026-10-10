from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [
    path("request_athlete_edit/<int:id>", request_athlete_edit, name="request_athlete_edit"),    
    path("my_edit_requests_list/", my_edit_requests_list, name="my_edit_requests_list"),
    path("athletes_to_edit/", athletes_to_edit, name="athletes_to_edit"),
    # path("review-edit-request/<uuid:request_id>/", review_edit_request, name="review_edit_request"),
    path("edit_request_detail/<uuid:request_id>/", edit_request_detail, name="edit_request_detail"),
    path("delete_athlete_edit/<uuid:id>", delete_athlete_edit, name="delete_athlete_edit"),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
