from django.shortcuts import render, redirect, get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.contrib import messages
from xhtml2pdf import pisa
from io import BytesIO
from .models import *
from .forms import *
from django.db import IntegrityError
from django.core.files.base import ContentFile
import base64


def trainee_add(request):
    if request.method == "POST":
        form = TraineesForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                new_trainee = form.save(commit=False)

                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        new_trainee.photo = data  # Assign cropped image
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "trainee_new.html", {"form": form})

                new_trainee.save()
                messages.success(request, "Trainee added successfully!")
                return redirect("addtrainee")

            except IntegrityError:
                messages.error(request, "There was an error saving the trainee.")
                return render(request, "trainee_new.html", {"form": form})

    else:
        form = TraineesForm()

    context = {"form": form}
    return render(request, "trainee_new.html", context)


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


from .filters import TraineeFilter  # Assume you have created this filter


def trainees(request):
    # Get all trainees
    trainees = Trainee.objects.all()

    # Apply the filter
    trainee_filter = TraineeFilter(request.GET, queryset=trainees)
    filtered_trainees = trainee_filter.qs

    if request.method == "POST":
        # Check which form was submitted
        if "Accreditation" in request.POST:
            template = get_template("acred.html")
            filename = "Asshu_Accreditation.pdf"
        elif "Certificate" in request.POST:
            template = get_template(
                "certificate_temaplate.html"
            )  # Your certificate template
            filename = "Filtered_Certificate.pdf"
        else:
            return HttpResponse("Invalid form submission")

        # Generate PDF
        context = {"trainees": filtered_trainees}
        html = template.render(context)

        # Create a PDF
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
        # Render the filter form
        return render(request, "trainees.html", {"filter": trainee_filter})


def trainee_details(request, id):
    trainee = Trainee.objects.get(id=id)

    context = {"trainee": trainee}
    return render(request, "trainee.html", context)


def trainee_update(request, id):
    trainee = get_object_or_404(Trainee, id=id)

    if request.method == "POST":
        form = TraineesForm(request.POST, request.FILES, instance=trainee)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainees information updated successfully!")
            return redirect("trainee", id=trainee.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TraineesForm(instance=trainee)

    context = {
        "form": form,
        "trainee": trainee,
    }
    return render(request, "update_trainee.html", context)


def trainee_delete(request, id):
    stud = Trainee.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("trainees")

    return render(request, "delete_trainee.html", {"obj": stud})


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
            "zone",
            "contact",
            "district",
            "region",
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in Trainee.objects.all():
        writer.writerow(
            [
                obj.id,
                obj.first_name,
                obj.last_name,
                obj.school,
                obj.contact,
                obj.zone,
                obj.district,
                obj.region,
            ]
        )  # Replace with your model's fields

    return response
