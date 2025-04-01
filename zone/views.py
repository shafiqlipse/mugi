from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Zone
from .models import Zonalchair
from enrollment.models import SchoolEnrollment
from school.models import School, Athlete, school_official
from django.core.paginator import Paginator
from enrollment.filters import SchoolEnrollmentFilter
from school.filters import AthleteFilter
# Create your views here.
def zonalchair_list(request):
    chairpersons = Zonalchair.objects.all()
    context={"chairpersons": chairpersons}
    return render(request, "zonalchair_list.html", context)
# Compare this snippet from usssa/zone/templates/zone/zonalchair_list.html: 

@login_required
def activate_zonalchair(request, id):
    zonalchair = get_object_or_404(Zonalchair, id=id)
    
    if zonalchair.status != "active":
        zonalchair.status = "active"
        zonalchair.save()
        messages.success(request, f"{zonalchair.fname} {zonalchair.lname} has been activated.")
    else:
        messages.info(request, "This zonal chair is already active.")

    return redirect("zonalchair_list") 

def zonalchair_dashboard(request):
    chairperson = get_object_or_404(Zonalchair, user=request.user)
    zone = get_object_or_404(Zone, id=chairperson.zone.id)
    districts = zone.district_set.all()
    schools = School.objects .filter(district__in=districts)
    schools_count = School.objects .filter(district__in=districts).count()
    athletes = Athlete.objects.filter(school__in=schools).count()
    context={"zone": zone, "districts": districts,  "schools_count": schools_count, "athletes": athletes}
    return render(request, "zonalchair_dashboard.html", context)

def zonalchair_schools(request):
    chairperson = get_object_or_404(Zonalchair, user=request.user)
    zone = get_object_or_404(Zone, id=chairperson.zone.id)
    districts = zone.district_set.all()
    schools = School.objects .filter(district__in=districts)
    context={"schools": schools}
    return render(request, "zonalchair_schools.html", context)

def zonalchair_athletes(request):
    chairperson = get_object_or_404(Zonalchair, user=request.user)
    zone = get_object_or_404(Zone, id=chairperson.zone.id)
    districts = zone.district_set.all()
    schools = School.objects .filter(district__in=districts)
    athletes = Athlete.objects.filter(school__in=schools).exclude(status="COMPLETED")

    # Apply filtering
    athlete_filter = AthleteFilter(request.GET, queryset=athletes)
    filtered_athletes = athlete_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_athletes, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_athletes = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "athletes": paginated_athletes,
        "athlete_filter": athlete_filter,
    }
    return render(request, "zonalchair_athletes.html", context)

def zonalchair_officials(request):
    chairperson = get_object_or_404(Zonalchair, user=request.user)
    zone = get_object_or_404(Zone, id=chairperson.zone.id)
    districts = zone.district_set.all()
    schools = School.objects .filter(district__in=districts)
    officials = school_official.objects.filter(school__in=schools)
    context={"officials": officials}
    return render(request, "zonalchair_officials.html", context)


def zonalchair_enrollments(request):
    chairperson = get_object_or_404(Zonalchair, user=request.user)
    zone = get_object_or_404(Zone, id=chairperson.zone.id)
    districts = zone.district_set.all()
    schools = School.objects .filter(district__in=districts)
    enrollments = SchoolEnrollment.objects.filter(school__in=schools)
    
    school_enroll_filter = SchoolEnrollmentFilter(request.GET, queryset=enrollments)
    filtered_enrolls = school_enroll_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_enrolls, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_enrolls = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "enrolls": paginated_enrolls,
        "school_enroll_filter": school_enroll_filter,
    }
    return render(request, "zonalchair_enrollments.html", context)

# Compare this snippet from usssa/zone/templates/zone/zonalchair_create.html:
