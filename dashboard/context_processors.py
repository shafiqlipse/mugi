from django.shortcuts import render
from support.models import Ticket


def tickets(request):
    
    tickets_count = Ticket.objects.all().exclude(status = 'Answered').count()
    return  {'tickets_count': tickets_count}


