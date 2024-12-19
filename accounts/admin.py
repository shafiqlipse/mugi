from django.contrib import admin
from accounts.models import *
from school.models import *
from training.models import *

# Register your models here.
admin.site.register(User)
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

# admin.site.register(school_official)
