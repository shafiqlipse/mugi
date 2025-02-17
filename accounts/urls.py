from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500


handler404 = custom_404_view
handler500 = custom_500_view
handler503 = custom_503_view

urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("confirm/", Confirm, name="confirm"),
    path('success/', success, name='success'),
    path("change_password/", change_password, name="change_password"),
    path("password-reset/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    
    # path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:id>', ticket, name='ticket'),
    path('tickets/', tickets, name='tickets'),
    path('support/', support, name='support'),
    path('tickets/create/', open_ticket, name='ticket_create'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
