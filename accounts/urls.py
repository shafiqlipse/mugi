from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from .zonal_views import *
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
    

    path("users_data/", users_data, name="users_data"),
    path("users/", users, name="users"),
    path("zonal_users/", zonal_users, name="zonal_users"),
    path('user/edit/<int:id>/', edit_user, name='edit_user'),
    # path('user/edit/<int:id>/', edit_user, name='edit_user'),
    
    path("zonalchair/", zonalchair_list, name="zonalchair_list"),
    path("dashboard/chair/", zonalchair_dashboard, name="zonalchair_dashboard"),
    path("zonalchair/<int:id>/", activate_zonalchair, name="zonalchair_activate"),
    path("zonalchair/schools/", zonalchair_schools, name="zonalchair_schools"),
    path("zonalchair/athletes/", zonalchair_athletes, name="zonalchair_athletes"),
    path("zonalchair/officials/", zonalchair_officials, name="zonalchair_officials"),
    path("zonalchair/enrollments/", zonalchair_enrollments, name="zonalchair_enrollments"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
