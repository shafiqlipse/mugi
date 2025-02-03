from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import *
from school.models import *
from training.models import *

class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_active", "is_school", "is_staff", "is_admin", "is_tech", "is_accounts", "school")  # Columns to display
    search_fields = ("username", "email", "school__name")  # Enables search
    list_filter = ("is_active", "is_school", "is_staff", "is_admin", "is_tech", "is_accounts", "school")  # Enables filtering

admin.site.register(User, UserAdmin)
admin.site.register(Discipline)
admin.site.register(Venue)
admin.site.register(Trainee)

admin.site.register(Sport)
admin.site.register(Championship)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(Athlete)
admin.site.register(School)
# admin.site.register(City)
admin.site.register(Zone)
admin.site.register(Classroom)



