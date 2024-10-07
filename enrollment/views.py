from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from xhtml2pdf import pisa
from io import BytesIO
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


from .filters import SchoolEnrollmentFilter  # Assume you have created this filter


def SchoolEnrollments(request):
    # Get school from user profile
    school = request.user.profile  # Assuming profile has school attribute

    # Get all enrollments for the school
    enrollments = SchoolEnrollment.objects.filter(school=school)

    if request.method == "POST":
        form = SchoolEnrollmentForm(request.POST, request.FILES)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.school = school
            enrollment.save()
            messages.success(request, "Enrollment created successfully!")
            return redirect("school_enrollments")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolEnrollmentForm()

    context = {"form": form, "enrollments": enrollments}
    return render(request, "school_enrolls.html", context)


def AllEnrollments(request):
    # Get all school_enrolls
    school_enrolls = SchoolEnrollment.objects.all()

    # Apply the filter
    school_enroll_filter = SchoolEnrollmentFilter(request.GET, queryset=school_enrolls)
    filtered_school_enrolls = school_enroll_filter.qs

    if request.method == "POST":
        # Check which form was submitted
        if "Accreditation" in request.POST:
            template = get_template("acred.html")
            filename = "Asshu_Accreditation.pdf"
        elif "Certificate" in request.POST:
            template = get_template("certificate_template.html")
            filename = "Filtered_Certificate.pdf"
        elif "Athletes" in request.POST:
            template = get_template("athletes_template.html")
            filename = "Athletes_List.pdf"
        else:
            return HttpResponse("Invalid form submission")

        # Prepare context with athletes data
        context = {
            "school_enrolls": filtered_school_enrolls,
            "athletes": [],  # Initialize empty list for athletes
        }

        # If generating athletes template, prepare the athletes data
        if "Athletes" in request.POST:
            for enrollment in filtered_school_enrolls:
                # Get athlete enrollments for this school enrollment
                athlete_enrollments = AthleteEnrollment.objects.filter(
                    school_enrollment=enrollment
                )
                # Collect all athletes from all athlete enrollments
                for athlete_enrollment in athlete_enrollments:
                    athletes = athlete_enrollment.athletes.all()
                    context["athletes"].extend(athletes)

        # Generate PDF
        html = template.render(context)
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")

        pdf_buffer.seek(0)

        # Return the PDF as a response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write(pdf_buffer.getvalue())
        return response
    else:
        # For GET request, prepare athletes data
        all_athletes = []
        for enrollment in filtered_school_enrolls:
            athlete_enrollments = AthleteEnrollment.objects.filter(
                school_enrollment=enrollment
            )
            for athlete_enrollment in athlete_enrollments:
                all_athletes.extend(athlete_enrollment.athletes.all())

        context = {"filter": school_enroll_filter, "athletes": all_athletes}

        return render(request, "enroll.html", context)


def remove_athlete(request, enrollment_id, athlete_id):
    athlete_enrollment = get_object_or_404(AthleteEnrollment, id=enrollment_id)
    athlete = get_object_or_404(Athlete, id=athlete_id)

    if request.method == "POST":
        athlete_enrollment.athletes.remove(athlete)
        return HttpResponseRedirect(
            reverse("school_enrollment", args=[athlete_enrollment.school_enrollment.id])
        )

    return redirect("school_enrollment", id=athlete_enrollment.school_enrollment.id)


def school_enrollment_details(request, id):
    school_enrollment = get_object_or_404(SchoolEnrollment, id=id)
    school = school_enrollment.school
    if request.method == "POST":
        form = AthleteEnrollmentForm(request.POST)
        if form.is_valid():
            athlete_enrollment = AthleteEnrollment.objects.create(
                school_enrollment=school_enrollment
            )
            athlete_enrollment.athletes.set(form.cleaned_data["athletes"])
            return HttpResponseRedirect(reverse("school_enrollment", args=[id]))
    else:
        form = AthleteEnrollmentForm()

    athlete_enrollments = AthleteEnrollment.objects.filter(
        school_enrollment=school_enrollment
    )
    all_athletes = Athlete.objects.filter(school=school)

    context = {
        "school_enrollment": school_enrollment,
        "form": form,
        "athlete_enrollments": athlete_enrollments,
        "all_athletes": all_athletes,
    }
    return render(request, "school_enroll.html", context)


def school_enrollment_update(request, id):
    school_enrollment = get_object_or_404(SchoolEnrollment, id=id)

    if request.method == "POST":
        form = SchoolEnrollmentForm(
            request.POST, request.FILES, instance=school_enrollment
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, "SchoolEnrollment information updated successfully!"
            )
            return redirect("school_enrollment", id=school_enrollment.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SchoolEnrollmentForm(instance=school_enrollment)

    context = {
        "form": form,
        "school_enrollment": school_enrollment,
    }
    return render(request, "update_school_enroll.html", context)


def school_enroll_delete(request, id):
    stud = SchoolEnrollment.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("school_enrollments")

    return render(request, "delete_school_enroll.html", {"obj": stud})


import csv
from django.http import HttpResponse


def export_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="data.csv"'

    # Create a CSV writer object using the HttpResponse as the file.
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "id",
            "first_name",
            "last_name",
            "school",
            "designation",
            "contact",
            "district",
            "region",
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in SchoolEnrollment.objects.all():
        writer.writerow(
            [
                obj.id,
                obj.first_name,
                obj.last_name,
                obj.school,
                obj.designation,
                obj.contact,
                obj.district,
                obj.region,
            ]
        )  # Replace with your model's fields

    return response


from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_html_email(subject, to_email, context):
    # Load the HTML content from a template
    html_content = render_to_string("email_template.html", context)

    # Plain text alternative for email clients that don't support HTML
    text_content = strip_tags(html_content)

    # Set up the email parameters
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text version
        from_email="your-email@gmail.com",
        to=[to_email],
    )

    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()


# View to handle the email sending
def send_email_view(request):
    if request.method == "POST":
        subject = "Important Updates"
        to_email = request.POST.get("email")  # Get email from POST data
        context = {
            "first_name": request.POST.get("first_name"),
            "action_url": request.POST.get("action_url"),
        }

        # Call function to send the email
        send_html_email(subject, to_email, context)

        # Return a success response
        return JsonResponse({"status": "Email sent successfully!"})

    # If not a POST request, return an error
    return JsonResponse({"status": "Invalid request method!"}, status=400)
