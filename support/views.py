from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from .forms import *



# Create your views here.


def open_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.sender = request.user
            ticket.save()
            return redirect('tickets')
        # Form remains populated with submitted data if invalid
    else:
        form = TicketForm()
    
    context = {'form': form}  # Fixed dictionary syntax
    return render(request, "support/open_ticket.html", context)

@login_required
def ticket(request, id):
    user = request.user

    # Who may see what:
    #   staff        -> only tickets in their department (superusers: everything)
    #   school users -> only tickets they sent
    # (If a school can have several users, filter by school instead of sender.)
    if user.is_staff:
        visible = Ticket.objects.for_staff(user)
    else:
        visible = Ticket.objects.filter(sender=user)

    # Get the selected ticket (404 if it isn't one this user may see)
    ticket = get_object_or_404(visible, id=id)

    # Sidebar tickets: same visibility rules, same topic, latest activity first
    tickets = (
        visible.select_related("sender")
        .filter(topic=ticket.topic)
        .order_by("-updated_at")
    )

    # Responses for this ticket
    responses = ticket.responses.select_related("author").order_by("-created_at")

    # Handle reply form
    if request.method == "POST":
        if ticket.status == "Closed":
            messages.error(request, "This ticket is closed.")
            return redirect("ticket", id=id)

        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.author = user
            response.save()  # TicketMessage.save() updates status and assignment
            return redirect("ticket", id=id)
    else:
        form = TicketResponseForm()

    context = {
        "ticket": ticket,        # The currently selected ticket (detail)
        "tickets": tickets,      # Sidebar list
        "responses": responses,  # All replies to the current ticket
        "form": form,            # Reply form
    }
    return render(request, "support/ticket.html", context)

def tickets(request):
    tickets = Ticket.objects.select_related("sender").filter(sender=request.user)
    context={
        'tickets': tickets,
    }
    return render(request, "support/tickets.html", context)

def answered_tickets(request):
    tickets = Ticket.objects.select_related("sender").filter(status="Answered")
    context={
        'tickets': tickets,
    }
    return render(request, "support/all_tickets.html", context)

def support(request):
    tickets = Ticket.objects.select_related("sender").all().exclude(status="Answered")
    context={
        'tickets': tickets,
    }
    return render(request, "support/support.html", context)


# Error pages