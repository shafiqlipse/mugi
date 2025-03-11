from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import *
from school.models import *
from training.models import *

class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_active", "is_school", "is_staff", "is_admin", "is_tech", "is_accounts", "school")  # Columns to display
    search_fields = ("username", "email", "school__name")  # Enables search
    list_filter = ("is_active", "is_school", "is_staff", "is_admin", "is_tech", "is_accounts", "school")  # Enables filtering

class AthleteAdmin(admin.ModelAdmin):  # Inherit from admin.ModelAdmin
    list_display = ("fname", "lname", "index_number", "gender", "classroom", "school", "date_of_birth")
    search_fields = ("fname", "lname", "index_number", "school__name")  # Use school__name instead of school
    list_filter = ("classroom", "gender", "school")
# Register your models here.
admin.site.register(Athlete, AthleteAdmin) 

class SchoolAdmin(admin.ModelAdmin):  # Inherit from admin.ModelAdmin
    list_display = ("name", "center_number", "emis_number", "district")
    search_fields =( "name", "center_number", "emis_number")  # Use school__name instead of school

class PaymentAdmin(admin.ModelAdmin):  # Inherit from admin.ModelAdmin
    list_display = ("school", "phone_number",  "status", "amount", "date")
    search_fields =( "school", "phone_number",  "status",)  # Use school__name instead of school

# Register your models here.
admin.site.register(School, SchoolAdmin) 
admin.site.register(Payment, PaymentAdmin) 

admin.site.register(User, UserAdmin)
admin.site.register(Discipline)
admin.site.register(Venue)
admin.site.register(Trainee)

admin.site.register(Sport)
admin.site.register(Championship)
admin.site.register(Region)
admin.site.register(District)


# admin.site.register(City)
admin.site.register(Zone)
admin.site.register(Classroom)


from .models import SystemStatus

@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ('closure_start', 'closure_end')
