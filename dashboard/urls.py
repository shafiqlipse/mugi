from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from accounts.views import *
from school.views import *


urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    # path("dashcore/", dashcore, name="dashcore"),
    path("users/", users, name="users"),
    path('user/edit/<int:id>/', edit_user, name='edit_user'),
    path("school-dashboard/", Dash, name="schooldash"),
    path("alltransfers/", AllTransfers, name="alltransfers"),
    path("pending_transfers/", Pending_Transfers, name="pending_transfers"),
    path("approved_transfers/", Approved_Transfers, name="approved_transfers"),
    path("championships/", championships, name="championships"),
    path("sport/", sports, name="sports"),
    # path("sport/", sports, name="sports"),
    path("announcement/", announcement, name="announcement"),
    path("announcements/", announcements, name="announcements"),
    path("edit_announcement/<int:id>", edit_announcement, name="edit_announcement"),
    path("delete_announcement/<int:id>", delete_announcement, name="delete_announcement"),
    # path("sport/", sports, name="sports"),
    path("accounts/", accounts, name="accounts"),
    path("payments/", payments, name="payments"),
    path("pending_payments/", pending_payments, name="pending_payments"),
    path("activate_payment/<int:id>", activate_payment, name="activate_payment"),
    path("payment_detail/<int:id>", payment_detail, name="payment_detail"),
    # path("delete_announcement/<int:id>", delete_announcement, name="delete_announcement"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
