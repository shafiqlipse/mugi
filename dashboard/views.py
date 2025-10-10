from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.decorators import admin_required
from school.models import *
from accounts.models import *
from transfers.models import *
from django.contrib import messages
from .forms import *
from .models import *
today = timezone.now().date()
from django.db.models import Count
from django.utils import timezone
from django.db.models import Q

# Filter schools created today
@login_required
def dashboard(request):
    today = timezone.now().date()  # Assuming timezone is set

    # Use a single query to get all counts
    enrollments_count = SchoolEnrollment.objects.count()
    transfers_count = TransferRequest.objects.all().count()
    approved_count = TransferRequest.objects.filter(status='Approved').count()
    schools_count = School.objects.count()
    officials_count = school_official.objects.count()
    athletes_count = Athlete.objects.count()

    # Get counts for today
    schools_today = School.objects.filter(created=today).count()
    athletes_today = Athlete.objects.filter(created=today).count()

    # Use annotate to aggregate counts of schools and athletes for each region
    regions = Region.objects.annotate(
        school_count=Count('zone__district__school'),
        athlete_count=Count('zone__district__school__athletes')
    )

    # Get the latest 5 schools and 6 athletes with related fields in one query
    schools = School.objects.select_related("district").order_by("-created")[:5]
    athletes = Athlete.objects.select_related("school").order_by("-created")[:5]

    context = {
        "enrollments_count": enrollments_count,
        "schools_count": schools_count,
        "transfers_count": transfers_count,
        "approved_count": approved_count,
        "officials_count": officials_count,
        "schools": schools,
        "athletes": athletes,
        "regions": regions,
        "athletes_count": athletes_count,
        "schools_today": schools_today,
        "athletes_today": athletes_today,
    }
    return render(request, "dashboard/overview.html", context)



# championships


# @admin_required
def championships(request):
    championships = Championship.objects.all()
    new_championship = None

    if request.method == "POST":
        sform = ChampionshipForm(request.POST, request.FILES)

        if sform.is_valid():
            new_championship = sform.save(commit=False)

            new_championship.save()
            return redirect("championships")
    else:
        sform = ChampionshipForm()
    context = {"championships": championships, "sform": sform}
    return render(request, "all/championships.html", context)


@admin_required
def championship_details(request, id):
    championship = get_object_or_404(Championship, id=id)

    context = {"championship": championship}
    return render(request, "all/championship.html", context)


@admin_required
def championship_update(request, id):
    championship = get_object_or_404(Championship, id=id)

    if request.method == "POST":
        form = ChampionshipForm(request.POST, request.FILES, instance=championship)
        if form.is_valid():
            form.save()
            messages.success(request, "Championship information updated successfully!")
            return redirect("championship", id=championship.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ChampionshipForm(instance=championship)

    context = {
        "form": form,
        "championship": championship,
    }
    return render(request, "all/update_championship.html", context)


@admin_required
def championship_delete(request, id):
    stud = Championship.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("championships")

    return render(request, "all/delete_championship.html", {"obj": stud})


# sports


def sports(request):
    sports = Sport.objects.all()
    new_sport = None

    if request.method == "POST":
        sform = SportForm(request.POST, request.FILES)

        if sform.is_valid():
            new_sport = sform.save(commit=False)

            new_sport.save()
            return redirect("sports")
    else:
        sform = SportForm()
    context = {"sports": sports, "sform": sform}
    return render(request, "sport/sports.html", context)


@admin_required
def sport_details(request, id):
    sport = Sport.objects.get(id=id)

    context = {"sport": sport}
    return render(request, "sport/sport.html", context)


@admin_required
def sport_update(request, id):
    sport = get_object_or_404(Sport, id=id)

    if request.method == "POST":
        form = SportForm(request.POST, request.FILES, instance=sport)
        if form.is_valid():
            form.save()
            messages.success(request, "Sport information updated successfully!")
            return redirect("sport", id=sport.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SportForm(instance=sport)

    context = {
        "form": form,
        "sport": sport,
    }
    return render(request, "sport/update_sport.html", context)


@admin_required
def sport_delete(request, id):
    stud = Sport.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("sports")

    return render(request, "sport/delete_sport.html", {"obj": stud})


# @transfer_required
@login_required
def AllTransfers(request):
    transfers = TransferRequest.objects.filter(status ='Accepted')
    
    context = {"transfers": transfers}
    return render(request, "all/transfers.html", context)

# @transfer_required
@login_required
def Pending_Transfers(request):
    transfers = TransferRequest.objects.filter(status ='Pending')
    
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)

@login_required
def Approved_Transfers(request):
    transfers = TransferRequest.objects.filter(status ='Approved')
    
    context = {"transfers": transfers}
    return render(request, "all/transfer_s.html", context)

def announcement_add(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'your_template.html', {'announcements': announcements})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.base import ContentFile
from .models import Announcement
from .forms import AnnouncementForm
import base64
from django.utils.timezone import now
from school.filters import PaymentFilter
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
@login_required
def announcement(request):
   
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                announce = form.save(commit=False)

                # Handle cropped image data for the "banner" field
                cropped_data = request.POST.get("banner_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f"banner.{ext}")
                        announce.banner = data
                    except (ValueError, TypeError) as e:
                        messages.error(request, "Invalid image data.")
                        return render(request, "all/announce.html", {"form": form})

                announce.save()
                messages.success(request, "Announcement added successfully!")
                return redirect("announcement")

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                return render(request, "all/anounce.html", {"form": form})

        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = AnnouncementForm()

    context = {"form": form}
    return render(request, "all/anounce.html", context)

@login_required
def announcements(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, "all/announcements.html", {"announcements": announcements})

@login_required
def edit_announcement(request, id):
    # Retrieve the existing announcement by ID
    announcement = get_object_or_404(Announcement, id=id)
    
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            try:
                updated_announcement = form.save(commit=False)

                # Handle cropped image data for the "banner" field
                cropped_data = request.POST.get("banner_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f"banner.{ext}")
                        updated_announcement.banner = data
                    except (ValueError, TypeError) as e:
                        messages.error(request, "Invalid image data.")
                        return render(
                            request, "all/anounce.html", {"form": form, "announcement": announcement}
                        )

                updated_announcement.save()
                messages.success(request, "Announcement updated successfully!")
                return redirect("announcements")  # Adjust to your announcement list view

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
                return render(request, "all/anounce.html", {"form": form, "announcement": announcement})

        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = AnnouncementForm(instance=announcement)

    context = {"form": form, "announcement": announcement}
    return render(request, "all/anounce.html", context)

@login_required
def delete_announcement(request, id):
    # Get the announcement by primary key
    announcement = get_object_or_404(Announcement, id=id)

    # Check if the user has permission to delete (e.g., only admins or the creator)
    if request.user.is_staff:  # Example of permission check
        announcement.delete()
        messages.success(request, "Announcement deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete this announcement.")

    return redirect('announcements') 

# ---------------Accounts-----------------
from enrollment.models import *
from django.db.models import Sum, Count, F

@login_required
def accounts(request):
    
    total_earnings = Payment.objects.filter(status="COMPLETED").aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending = Payment.objects.filter(status="PENDING").count()
    total_completed = Payment.objects.filter(status="COMPLETED").count()
    total_schools = Payment.objects.values('school').distinct().count()
    total_athletes = Payment.objects.values('athletes').distinct().count()

    recent_transactions = Payment.objects.order_by('-created_at')[:10]  # Last 10 transactions
    
    schools_per_champs = SchoolEnrollment.objects.values('championship__name').annotate(count=Count('id')).order_by('-count')
    
    athletes_per_champ = AthleteEnrollment.objects.values('school_enrollment__championship__name').annotate(count=Count('athletes')).order_by('-count')
    
    school_per_sport = SchoolEnrollment.objects.values('sport__name').annotate(count=Count('id')).order_by('-count')
    
    athletes_per_sport = AthleteEnrollment.objects.values('school_enrollment__sport__name').annotate(count=Count('athletes')).order_by('-count')
    
    schools_per_level = SchoolEnrollment.objects.values('level').annotate(count=Count('id')).order_by('-count')
    
    schools_with_highest_enrollments = AthleteEnrollment.objects.values('school_enrollment__school__name').annotate(total_athletes=Count('athletes')).order_by('-total_athletes')[:10]
    
    most_enrolls = AthleteEnrollment.objects.values('enrolled_by__username').annotate(count=Count('id')).order_by('-count')
    
    most_recent_school_enrolls = SchoolEnrollment.objects.order_by('-enrollment_date')[:10]
    
    recent_enrolled_athletes = AthleteEnrollment.objects.order_by('-enrollment_date')[:10]
    
    schools_per_champs_list = SchoolEnrollment.objects.values('championship__name').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'total_earnings': total_earnings,
        'total_pending': total_pending,
        'total_completed': total_completed,
        'total_schools': total_schools,
        'total_athletes': total_athletes,
        'recent_transactions': recent_transactions,
        # 'recent_transactions': recent_transactions,
        'schools_per_champs': schools_per_champs,
        'athletes_per_champ': athletes_per_champ,
        'school_per_sport': school_per_sport,
        'athletes_per_sport': athletes_per_sport,
        'schools_per_level': schools_per_level,
        'schools_with_highest_enrollments': schools_with_highest_enrollments,
        'most_enrolls': most_enrolls,
        'most_recent_school_enrolls': most_recent_school_enrolls,
        'recent_enrolled_athletes': recent_enrolled_athletes,
        'schools_per_champs_list': schools_per_champs_list,
    }
    return render(request, "dashboard/accounts.html", context)

@login_required
def payments(request):
    pawyments = Payment.objects.select_related("school").filter(status="COMPLETED").order_by('-created_at')    
    
    # Apply filtering
    payments_filter = PaymentFilter(request.GET, queryset=pawyments)
    filtered_payments = payments_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_payments, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_payments = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": paginated_payments,
        "payment_filter": payments_filter,
    }
   
    return render(request, "dashboard/payments.html", context)

@login_required
def pending_payments(request):
    pawyments = Payment.objects.select_related("school").filter(status="PENDING").order_by('-created_at')  
    payments_filter = PaymentFilter(request.GET, queryset=pawyments)
    filtered_payments = payments_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_payments, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_payments = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": paginated_payments,
        "payment_filter": payments_filter,
    }
    # Pass the filter to the context for rendering the filter form
 

    return render(request, "dashboard/pending.html", context)

@login_required
def activate_payment(request, id):
    payment = get_object_or_404(Payment,id=id)
    payment.status = "COMPLETED"
    payment.save() # Save the updated status
    messages.success(request, f"Payment {payment} is now {payment.status}.")
    return redirect("pending_payments")
#     context = {"payment": payment}


@login_required
def payment_detail(request, id):
    payment = get_object_or_404(Payment,id=id)
    context = {"payment": payment}
    return render(request, "dashboard/payment_detail.html", context)
   
#     context = {"payment": payment}


@login_required
def transactions(request):
    user = request.user
    school = user.school
    payments = Payment.objects.select_related("school").filter(status="COMPLETED", school=school).order_by('-created_at')  
    

    # Pass the filter to the context for rendering the filter form
    context = {
        "payments": payments,
    }
    # Pass the filter to the context for rendering the filter form
 

    return render(request, "dashboard/complete.html", context)




from django.db.models import Sum


def payment_summery(request):
    completed_payments = Payment.objects.filter(status='COMPLETED')

    school_totals = (
        completed_payments
        .values('school__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('school__name')
    )

    district_totals = (
        completed_payments
        .values('school__district__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('school__district__name')
    )

    zone_totals = (
        completed_payments
        .values('school__district__zone__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('school__district__zone__name')
    )

    context = {
        'school_totals': school_totals,
        'district_totals': district_totals,
        'zone_totals': zone_totals,
    }
    return render(request, 'dashboard/summery.html', context)
