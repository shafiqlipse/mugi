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
                return redirect("school_dashboard")
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
            messages.error(request, "Error in login. Please check your credentials. Note that Passwords are case sensitive")
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
    success_url = reverse_lazy("login")


def success(request):
    return render(request, "accounts/success.html")



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

from django.core.paginator import Paginator
from django.db.models import Count, Q
# schools

@staff_required
def users_data(request):
    """Handle AJAX DataTables request for large datasets"""
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get("search[value]", "").strip()

        # Filter base queryset
        users_query = User.objects.filter(is_school=True).select_related("school")

        # Apply search filters
        if search_value:
            users_query = users_query.filter(
                Q(username__icontains=search_value) |
                Q(email__icontains=search_value) |
                Q(school__name__icontains=search_value) |
                Q(school__emis_number__icontains=search_value)
            )

        # Pagination
        paginator = Paginator(users_query, length)
        page_number = (start // length) + 1
        users_page = paginator.get_page(page_number)

        data = []
        for user in users_page:
            school = getattr(user, 'school', None)
            name = school.name if school else "No School"
            emis = school.emis_number if school else "N/A"

            data.append({
                "username": user.username,
                "email": user.email,
                "school_profile": f"{name} | {emis}",
                "actions": f"""
                    <a href="/auth/user/edit/{user.id}/" class="btn btn-warning btn-sm">Edit</a>
                """,
            })

        response = {
            "draw": draw,
            "recordsTotal": User.objects.filter(is_school=True).count(),
            "recordsFiltered": users_query.count(),
            "data": data,
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# schools list, tuple or array
@staff_required
def users(request):
    
    users = User.objects.select_related("school").filter(is_school=True)

    context = {
        "users": users,
       
    }
    return render(request, "accounts/users.html", context)


@staff_required
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
