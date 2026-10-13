from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .filters import *
from django.contrib import messages
from accounts.decorators import *
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.conf import settings
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.db.models import F


def school_new(request):
    if request.method == "POST":
        form = SchoolProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                school = form.save(commit=False)

                # Handle cropped and resized images
                school.save()
                messages.success(request, "School profile created successfully!")
                return redirect("confirm")
            except IntegrityError as e:
                if "EMIS" in str(e):
                    messages.error(
                        request, "A school with this EMIS number already exists."
                    )
                else:
                    messages.error(
                        request,
                        "An error occurred while saving the school. Please fill all required fields.",
                    )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SchoolProfileForm()

    regions = Region.objects.all()
    context = {
        "form": form,
        "regions": regions,
    }
    return render(request, "school/newschool.html", context)


@login_required(login_url="login")
def school_update(request, id):
    school = get_object_or_404(School, id=id)

    if request.method == "POST":
        form = SchoolEditForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School information updated.")
            return redirect("schools")
    else:
        form = SchoolEditForm(instance=school)

    return render(request, "school/school_edit.html", {"form": form, "school": school})


# @staff_required
@login_required(login_url="login")
def school_detail(request, id):
    school = get_object_or_404(School, id=id)
    officials = school_official.objects.select_related("school").filter(school_id=id)
    # enrollments = SchoolEnrollment.objects.filter(school=school)
    athletes = Athlete.objects.select_related("school").filter(school_id=id).exclude(status="COMPLETED")

    context = {
        "school": school,
        "athletes": athletes,
        "officials": officials,
        # "enrollments": enrollments,
    }
    return render(request, "school/school.html", context)


@staff_required
def school_data_view(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "").strip()

    # Filtering
    schools = School.objects.select_related("district__zone")

    if search_value:
        schools = schools.filter(
            Q(name__icontains=search_value) |
            Q(center_number__icontains=search_value) |
            Q(district__name__icontains=search_value) |
            Q(district__zone__name__icontains=search_value)
        )

    total_records = School.objects.count()
    filtered_records = schools.count()

    # Pagination
    paginator = Paginator(schools, length)
    page_number = (start // length) + 1
    page = paginator.get_page(page_number)

    # Build response data
    data = []
    for school in page.object_list:
        data.append({
            "id": school.id,
            "name": school.name,
            "center_number": school.center_number,
            "district": school.district.name if school.district else "",
            "zone": school.district.zone.name if school.district and school.district.zone else "",
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    })
    
    
    
# @staff_required
@login_required(login_url="login")
def Schools(request):
    schools = School.objects.select_related("district__zone").order_by("-created")  # Remove slicing

    schools_filter = SchoolFilter(request.GET, queryset=schools)
    filtered_schools = schools_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_schools, 10)  # Show 10 schools per page
    page_number = request.GET.get("page")
    paginated_schools = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "schooles": paginated_schools,  # Ensure the correct variable name in the template
        "school_filter": schools_filter,
    }

    return render(request, "school/schools.html", context)



# # School delete......................................................
@login_required(login_url="login")
def DeleteSchool(request, id):
    stud = School.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("schools")

    return render(request, "school/deletesch.html", {"obj": stud})


# # Athletes Views......................................................
# # Athletes Views......................................................
# # Athletes Views......................................................
# # Athletes Views......................................................




@login_required(login_url="login")
def newAthlete(request):
    if request.method == "POST":
        form = NewAthleteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_athlete = form.save(commit=False)
                    new_athlete.school = request.user.school
                    new_athlete.save()
                    messages.success(request, "Athlete added successfully!")
                    return redirect('athletes')  # Redirect to your athlete list view

            except IntegrityError:
                messages.error(request, "Index number already exists")
            except Exception as e:
                messages.error(request, f"Server error: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    # GET request or form errors
    form = NewAthleteForm()
    return render(request, "athletes/new_athletes.html", {"form": form})


# schools list, tuple or array
@staff_required
def athlete_data_view(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = Athlete.objects.select_related('school').exclude(status="COMPLETED")

    total = queryset.count()

    if search_value:
        queryset = queryset.filter(
            Q(fname__icontains=search_value) |
            Q(lname__icontains=search_value) |
            Q(index_number__icontains=search_value) |
            Q(school__name__icontains=search_value)  # optionally include school name
        ) 

    filtered_total = queryset.count()

    data = list(
        queryset[start:start + length].values(
            'id',
            'fname',
            'lname',
            'index_number',
            'gender',
            'id',
            'status',
            'classroom',
            school_name=F('school__name'),
        )
    )

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_total,
        'data': data,
    })
    
    
def all_athletes(request):
    
    athletes_queryset = Athlete.objects.select_related("school").all().exclude(status="COMPLETED")

    context = {
        "athletes": athletes_queryset,

    }
    return render(request, "athletes/all_athletes.html", context)


# schools list, tuple or array

@staff_required
def archives_data_view(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = Athlete.objects.select_related("school").filter(status__iexact="completed")

    total = queryset.count()

    if search_value:
        queryset = queryset.filter(
            Q(fname__icontains=search_value) |
            Q(lname__icontains=search_value) |
            Q(index_number__icontains=search_value) |
            Q(school__name__icontains=search_value)  # optionally include school name
        )

    filtered_total = queryset.count()

    data = list(
        queryset[start:start + length].values(
            'id',
            'fname',
            'lname',
            'index_number',
            'gender',
            'status',
            'classroom',
            school_name=F('school__name'),
        )
    )

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered_total,
        'data': data,
    })
    
@staff_required
def archives(request):

    archives_list = Athlete.objects.select_related("school").filter(status__iexact="completed")
    # Apply filtering

    context = {
        "archives_list": archives_list,
    }
    return render(request, "athletes/archives.html", context)

@login_required
def AthleteUpdate(request, id):
    athlete = get_object_or_404(Athlete, id=id)

    if request.method == "POST":
        form = NewAthleteForm(request.POST, request.FILES, instance=athlete)
        if form.is_valid():
            try:
                new_athlete = form.save(commit=False)

                # Handle cropped photo from blob
                cropped_file = request.FILES.get("cropped_photo")
                if cropped_file:
                    new_athlete.photo = cropped_file

                new_athlete.save()
                messages.success(request, "Updated successfully!")
                return redirect("allathletes")

            except IntegrityError:
                messages.error(request, "There was an error saving the trainee.")
                return render(request, "trainee_new.html", {"form": form})
    else:
        form = NewAthleteForm(instance=athlete)

    context = {
        "form": form,
        "athlete": athlete,
    }
    return render(request, "athletes/new_athletes.html", context)

# # Athletes details......................................................

 

# # Athletes details......................................................
@login_required
def AthleteDetail(request, id):
    # Fetch the athlete object or return a 404 error
    athlete = get_object_or_404(Athlete, id=id)
    
    # Initialize variables
    new_screen = None
    dform = ScreenForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and dform.is_valid():
        # Save the form and associate it with the athlete and user
        new_screen = dform.save(commit=False)
        new_screen.athlete = athlete
        new_screen.screener = request.user
        new_screen.save()

        # Update athlete status to COMPLETED
        athlete.status = "COMPLETED"
        athlete.save()

        # Redirect to the athlete detail page
        return HttpResponseRedirect(reverse("athlete", args=[athlete.id]))

    # Calculate the athlete's age
    today = datetime.date.today()
    age = (
        today.year
        - athlete.date_of_birth.year
        - ((today.month, today.day) < (athlete.date_of_birth.month, athlete.date_of_birth.day))
    )

    context = {
        "athlete": athlete,
        "age": age,  # Pass the calculated age to the template
        "dform": dform,  # Pass the form to the template
    }

    return render(request, "athletes/athlete.html", context)


@login_required(login_url="login")
def athletes(request):
    user = request.user

    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "athletes/athletes.html", {"athletes": []})


    athletes = (
        Athlete.objects
        .filter(school=school_profile)
        .exclude(status="COMPLETED")
        .values("id", "fname", "lname", "index_number", "date_of_birth", "gender", "classroom", "status")
    )

    return render(request, "athletes/athletes.html", {"athletes": athletes})

def red_athletes(request):
    user = request.user
    
    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "athletes/athletes.html", {"athletes": []})

    athletes = (
        Athlete.objects
        .filter(school=school_profile, status="ACTIVE")
         .values("id", "fname", "lname", "index_number","date_of_birth", "gender","classroom")  # Fetch only id and name
    )
    

    context = {
        "athletes": athletes,
    }

    return render(request, "athletes/dathletes.html", context)


# # Athletes details......................................................
@login_required
def Screened(request):
    screens = Screening.objects.select_related("athlete").all()
    screens_filter = ScreenFilter(request.GET, queryset=screens)
    filtered_screens = screens_filter.qs  # Get the filtered queryset

    # Paginate filtered results
    paginator = Paginator(filtered_screens, 10)  # Show 10 athletes per page
    page_number = request.GET.get("page")
    paginated_screens = paginator.get_page(page_number)

    # Pass the filter to the context for rendering the filter form
    context = {
        "screens": paginated_screens,
        "screens_filter": screens_filter,
    }
    # Pass the filter to the context for rendering the filter form
 

    return render(request, "athletes/screens.html", context)

# # Athletes details......................................................
@admin_required(login_url="login")
def DeleteAthlete(request, id):
    stud = Athlete.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("allathletes")

    return render(request, "athletes/delete_ath.html", {"obj": stud})


@login_required(login_url="login")
def athlete_list(request):
    athletes = Athlete.objects.select_related("school").all()
    context = {"athletes": athletes}
    return render(request, "school/athlete_list.html", context)


# # School delete......................................................
# # School delete......................................................




@school_required
def Official(request):

    if request.method == "POST":
        form = OfficialForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                official = form.save(commit=False)

                # Assign the school from the user profile
                official.school = request.user.school


                official.save()
                messages.success(request, "official added successfully!")
                return redirect("officials")

            except IntegrityError as e:
                if "lin" in str(e).lower():
                    messages.error(
                        request,
                        "An official with this Learner Identification Number (LIN) already exists.",
                    )
                else:
                    messages.error(request, f"Error adding official: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error adding official: {str(e)}")
        else:
            # Form validation error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        form = OfficialForm()
    context = {"form": form}
    return render(request, "officials/NOfficial.html", context)



@login_required(login_url="login")
def school_offs(request):
    user = request.user

    # Check if the user has a school profile
    school_profile = getattr(user, "school", None)
    if not school_profile:
        return render(request, "officials/officials.html", {"school_offs": []})
        # Fetch school officials for the user's school, excluding inactive ones
    school_offs = (
            school_official.objects
            .select_related("school")  # Optimize by fetching school data in one query
            .filter(school=user.school)  # Directly filter by the school object
            .exclude(status="Inactive")  # Exclude inactive officials
        )

    context = {
        "school_offs": school_offs,
    }

    return render(request, "officials/officials.html", context)

@login_required(login_url="login")
def update_official(request, id):
    official = get_object_or_404(school_official, id=id)
    original_school = official.school # Store the original school for validation
    if request.method == "POST":
        form = OfficialForm(request.POST, request.FILES, instance=official)
        if form.is_valid():
            try:
                updated_official = form.save(commit=False)

                # Ensure the school is set to current user's school
                updated_official.school = original_school

                # Handle cropped image data if present
                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        updated_official.photo = data
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "officials/NOfficial.html", {"form": form, "update": True})

                updated_official.save()
                messages.success(request, "Official updated successfully!")
                return redirect("officials")

            except IntegrityError as e:
                if "nin" in str(e).lower():
                    messages.error(request, "An official with this NIN already exists.")
                else:
                    messages.error(request, f"Integrity error: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error updating official: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = OfficialForm(instance=official)

    return render(request, "officials/NOfficial.html", {"form": form, "update": True})


# # Athletes details......................................................
@login_required(login_url="login")
def OfficialDetail(request, id):
    official = get_object_or_404(school_official, id=id)
    relatedathletes = school_official.objects.filter(school=official.school).exclude(
        id=id
    )

    context = {
        "official": official,
        "relatedathletes": relatedathletes,
        # "breadcrumbs": breadcrumbs,
    }

    return render(request, "officials/official.html", context)


@login_required
def activate_official(request, id):
    official = get_object_or_404(school_official,id=id)
    official.status = "Active"
    official.save() # Save the updated status
    messages.success(request, f"Official {official.fname} is now {official.status}.")
    return redirect("officials")
#     context = {"payment": payment}

@login_required
def deactivate_official(request, id):
    official = get_object_or_404(school_official,id=id)
    official.status = "Inactive"
    official.save() # Save the updated status
    messages.error(request, f"Official {official.fname} has been deleted successfully.")
    return redirect("officials")
#     context = {"payment": payment}


# # Athletes details......................................................
@login_required(login_url="login")
def DeleteOfficial(request, id):
    stud = school_official.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("officials")

    return render(request, "officials/delete_official.html", {"obj": stud})



# # School delete......................................................
from payments.services import *
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
# Payments and activateion for registration
FEE_PER_ATHLETE = Decimal("3000")
import re
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect

from payments.services import create_and_initiate_payment
from .models import RegistrationPayment
from .forms import PaymentForm

AMOUNT_PER_ATHLETE = 3000
ADDITIONAL_FEE = 500  # confirm this is still a valid charge


def payment_view(request):
    school = request.user.school

    if request.method == 'POST':
        form = PaymentForm(request.POST, school=school)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            athletes = form.cleaned_data['athletes']

            if not re.match(r'^(073|075|074|070)\d{7}$', phone_number):
                messages.error(request, "Phone number must be a valid Airtel money number.")
                return render(request, 'payments/payment_form.html', {'form': form})

            if not athletes:
                messages.error(request, "You must select at least one athlete.")
                return render(request, 'payments/payment_form.html', {'form': form})

            total_amount = (athletes.count() * AMOUNT_PER_ATHLETE) + ADDITIONAL_FEE

            def link_registration(payment):
                rp = RegistrationPayment.objects.create(payment=payment, school=school)
                rp.athletes.set(athletes)

            try:
                payment, success, response = create_and_initiate_payment(
                    payment_type='REGISTRATION',
                    amount=total_amount,
                    phone_number=phone_number,
                    related_obj_setter=link_registration,
                )
            except Exception as e:
                airtel_logger.error(f"Payment failed for {school}: {str(e)}", exc_info=True)
                messages.error(request, "An error occurred while processing the payment. Please try again.")
                return render(request, 'payments/payment_form.html', {'form': form})

            if not success:
                messages.error(request, "Payment could not be initiated. Please try again.")
                return render(request, 'payments/payment_form.html', {'form': form})

            messages.success(request, f"Payment of UGX {total_amount} initiated — check your phone to approve.")
            airtel_logger.info(f"Payment initiated: School={school}, Amount={total_amount}, Phone={phone_number}, TxID={payment.transaction_id}")

            return redirect('payments:status', transaction_id=payment.transaction_id)

    else:
        form = PaymentForm(school=school)

    return render(request, 'payments/payment_form.html', {'form': form})



@require_POST
def initiate_registration_payment(request, school_id):
    school = get_object_or_404(School, id=school_id)
    athlete_ids = request.POST.getlist('athlete_ids')
    athletes = Athlete.objects.filter(id__in=athlete_ids, school=school).exclude(status='ACTIVE')

    if not athletes.exists():
        messages.error(request, "No eligible athletes selected for registration.")
        return redirect('schools:registration_detail', school_id=school.id)

    amount = FEE_PER_ATHLETE * athletes.count()
    phone_number = request.POST['phone_number']

    def link_registration(payment):
        rp = RegistrationPayment.objects.create(payment=payment, school=school)
        rp.athletes.set(athletes)

    payment, success, response = create_and_initiate_payment(
        payment_type='REGISTRATION',
        amount=amount,
        phone_number=phone_number,
        related_obj_setter=link_registration,
    )

    if not success:
        messages.error(request, "Payment could not be initiated. Please try again.")
        return redirect(reverse('payment_success', args=[payment.transaction_id])) 

    return redirect(reverse('payment_success', args=[payment.transaction_id])) 

    
def payment_success(request, transaction_id):
    payment = Payment.objects.filter(transaction_id=transaction_id).first()
    
    if not payment:
        return render(request, 'payment_failed.html', {'error': 'Transaction not found'})

    return render(request, 'payment_success.html', {
        'amount': payment.amount,
        'transaction_id': payment.transaction_id,
        'timestamp': payment.created_at,  # Make sure your Payment model has `created_at`
    })
    