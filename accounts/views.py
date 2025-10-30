from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from accounts.decorators import school_required, anonymous_required, staff_required
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.contrib import messages

# from .forms import SchoolRegistrationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import *


@login_required
def edit_user(request, id=None):
    if id:
        # Fetch the user to edit by their ID
        user = get_object_or_404(User, id=id)
    else:
        # Default to the logged-in user if no ID is provided
        user = request.user

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "The profile was updated successfully.")
            return redirect("users")
    else:
        form = UserEditForm(instance=user)

    return render(request, "accounts/edit_user.html", {"form": form, "id": user.id})


# from accounts.forms import AthleteFilterForm


# @staff_required
# def school_registration(request):
#     if request.method == "POST":
#         form = SchoolRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(
#                 commit=False
#             )  # Create the user object without saving to the database
#             user.is_school = True  # Set is_school to True
#             user.save()  # Save the user object with is_school set to True

#             # Log in the user
#             login(request, user)

#             return redirect("confirmation")
#     else:
#         form = SchoolRegistrationForm()
#     return render(request, "register.html", {"form": form})


# Create your views here.
@anonymous_required
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_school:
                messages.success(request, "School login successful.")
                return redirect("schooldash")
            elif user.is_admin:
                messages.success(request, "Officer login successful.")
                return redirect("dashboard")
            
            elif user.is_zone:
                messages.success(request, "Officer login successful.")
                return redirect("zonalchair_dashboard")
            else:
                messages.success(request, "Login successful.")
                return redirect(
                    "dashboard"
                )  # Adjust the URL name for your dashboard view
        else:
            messages.error(request, "Error in login. Please check your credentials.")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})


def user_logout(request):
    # if user.is_authenticated:
    logout(request)
    return redirect("login")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to maintain the user's login status
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("success")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "auth/change_password.html", {"form": form})


def Confirm(request):

    return render(request, "accounts/confirm.html")





from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "auth/password_reset.html"
    email_template_name = "auth/password_reset_email.html"
    subject_template_name = "auth/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("home")


def success(request):
    return render(request, "accounts/success.html")

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
    # Get the selected ticket
    ticket = get_object_or_404(Ticket, id=id)

    # Sidebar tickets: all user's tickets ordered by latest update
    tickets = Ticket.objects.select_related("sender").filter(sender=request.user, topic=ticket.topic).order_by('-created_at')

    # Responses for this ticket
    responses = ticket.responses.all().order_by('-created_at')

    # Handle reply form
    if request.method == 'POST':
        form = TicketResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ticket = ticket
            response.responder = request.user
            response.save()
            return redirect('ticket', id=id)
    else:
        form = TicketResponseForm()

    context = {
        'ticket': ticket,       # The currently selected ticket (detail)
        'tickets': tickets,     # List of all tickets (sidebar)
        'responses': responses, # All replies to the current ticket
        'form': form,           # Reply form
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
def custom_404_view(request, exception=None):
    return render(request, 'Pages/404.html', status=404)

def custom_500_view(request):
    return render(request, 'Pages/500.html', status=500)

def custom_503_view(request):
    return render(request, 'Pages/503.html', status=503)



def offline_view(request):
    return render(request, "Pages/offline.html")

# if SystemStatus.is_system_closed():
#     # Disable features
#     print("System is currently closed")

@login_required
def book_appointment(request):
    appointments = Appointment.objects.filter(client=request.user.school).select_related('championship')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user.school
            appointment.save()
            return redirect('appointment_success')
    else:
        form = AppointmentForm()
        
    context={
        'form': form,
        'appointments': appointments,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def appointment_success(request):
    return render(request, 'appointments/appointment_success.html')


def appointments(request):
    appointments = Appointment.objects.all().select_related('championship')
    context = {"appointments": appointments}
    return render(request, 'appointments/appointments.html', context)