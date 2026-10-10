from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


urlpatterns = [

    
    # path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:id>', ticket, name='ticket'),
    path('tickets/', tickets, name='tickets'),
    path('answered_tickets/', answered_tickets, name='answered_tickets'),
    path('support/', support, name='support'),
    path('tickets/create/', open_ticket, name='ticket_create'),
    

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
