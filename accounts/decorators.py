from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def school_required(view_func):
    @login_required(login_url="login")
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_school:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "auth/login.html")  # You can customize this template

    return _wrapped_view


def admin_required(login_url="login"):
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_admin:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "auth/login.html")  # You can customize this template

        return _wrapped_view

    return decorator

# def transfer_required(login_url="login"):
#     def decorator(view_func):
#         @wraps(view_func)
#         @login_required(login_url=login_url)
#         def _wrapped_view(request, *args, **kwargs):
#             if request.user.is_tech:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return render(request, "login.html")  # You can customize this template

#         return _wrapped_view

#     return decorator


def staff_required(view_func):
    @login_required(login_url="login")
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "auth/login.html")  # You can customize this template

    return _wrapped_view


def anonymous_required(view_func):
    """
    Decorator to ensure that the view is only accessible to anonymous users (not logged in).
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user

            # Check user roles and redirect accordingly
            if getattr(user, 'is_school', False):
                messages.success(request, "School login successful.")
                return redirect("schooldash")

            else:
                messages.success(request, "Login successful.")
                return redirect("dashboard")
        else:
            # If the user is not authenticated, allow access to the view
            return view_func(request, *args, **kwargs)

    return _wrapped_view

