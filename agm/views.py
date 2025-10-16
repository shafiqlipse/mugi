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
from django.db import transaction
from django.http import JsonResponse

def delegate_add(request):
    if request.method == "POST":
        form = DelegatesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    delegate = form.save(commit=False)
                    delegate.save()
                    messages.success(request, "Delegate registered successfully.")
                    return redirect("adddelegate")  # reload same page
            except IntegrityError:
                messages.error(request, "A delegate with this index number already exists.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DelegatesForm()

    return render(request, "delegate_new.html", {"form": form})




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


from .filters import DelegateFilter  # Assume you have created this filter


def delegates(request):
    # Get all delegates
    delegates = Delegates.objects.all()

    # Apply the filter
    delegate_filter = DelegateFilter(request.GET, queryset=delegates)
    alldelegates = delegate_filter.qs

    if request.method == "POST":
        # Check which form was submitted
        if "Accreditation" in request.POST:
            template = get_template("acred.html")
            filename = "Delegate_Accreditation.pdf"
        elif "Certificate" in request.POST:
            template = get_template(
                "certificate_temaplate.html"
            )  # Your certificate template
            filename = "Filtered_Certificate.pdf"
        else:
            return HttpResponse("Invalid form submission")

        # Generate PDF
        context = {"alldelegates": alldelegates}
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
        return render(request, "delegates.html", {"delegate_filter": delegate_filter})


def delegate_details(request, id):
    delegate = Delegates.objects.get(id=id)

    context = {"delegate": delegate}
    return render(request, "delegate.html", context)


def delegate_update(request, id):
    delegate = get_object_or_404(Delegates, id=id)

    if request.method == "POST":
        form = DelegatesForm(request.POST, request.FILES, instance=delegate)
        if form.is_valid():
            form.save()
            messages.success(request, "Delegates information updated successfully!")
            return redirect("delegate", id=delegate.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DelegatesForm(instance=delegate)

    context = {
        "form": form,
        "delegate": delegate,
    }
    return render(request, "update_delegate.html", context)


def delegate_delete(request, id):
    stud = Delegates.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("delegates")

    return render(request, "delete_delegate.html", {"obj": stud})


import csv
from django.http import HttpResponse


def export_dcsv(request):
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
            "email",
            "zone",
            "contact",
            "district",
            "region",
        ]
    )  # Replace with your model's fields

    # Write data rows
    for obj in Delegates.objects.all():
        writer.writerow(
            [
                obj.id,
                obj.first_name,
                obj.last_name,
                obj.school,
                obj.email,
                obj.contact,
                obj.zone,
                obj.district,
                obj.region,
            ]
        )  # Replace with your model's fields

    return response





def comiser_add(request):
    if request.method == "POST":
        form = ComisersForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                new_comiser = form.save(commit=False)

                cropped_data = request.POST.get("photo_cropped")
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(";base64,")
                        ext = format.split("/")[-1]
                        data = ContentFile(
                            base64.b64decode(imgstr), name=f"photo.{ext}"
                        )
                        new_comiser.photo = data  # Assign cropped image
                    except (ValueError, TypeError):
                        messages.error(request, "Invalid image data.")
                        return render(request, "comiser/comiser_new.html", {"form": form})

                new_comiser.save()
                messages.success(request, "Comiser added successfully!")
                return redirect("addcomiser")

            except IntegrityError:
                messages.error(request, "There was an error saving the comiser.")
                return render(request, "comiser/comiser_new.html", {"form": form})

    else:
        form = ComisersForm()

    context = {"form": form}
    return render(request, "comiser/comiser_new.html", context)


def generate_accreditation_pdf(request):
    comisers = Comiser.objects.all()

    # Load the template
    template = get_template("comiser/acred.html")
    context = {
        "comisers": comisers,
         # in case you need it for images
    }

    html = template.render(context)
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Error generating PDF <pre>" + html + "</pre>")

    pdf_buffer.seek(0)
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Comiser_Accreditation.pdf"'
    return response

def comisers(request):
    # Get all comisers
    comisers = Comiser.objects.all()

    return render(request, "comiser/comisers.html", {"comisers": comisers})


def comiser_details(request, id):
    comiser = Comiser.objects.get(id=id)

    context = {"comiser": comiser}
    return render(request, "comiser/comiser.html", context)


def comiser_update(request, id):
    comiser = get_object_or_404(Comiser, id=id)

    if request.method == "POST":
        form = ComisersForm(request.POST, request.FILES, instance=comiser)
        if form.is_valid():
            form.save()
            messages.success(request, "Comisers information updated successfully!")
            return redirect("comiser", id=comiser.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ComisersForm(instance=comiser)

    context = {
        "form": form,
        "comiser": comiser,
    }
    return render(request, "comiser/update_comiser.html", context)


def comiser_delete(request, id):
    stud = Comiser.objects.get(id=id)
    if request.method == "POST":
        stud.delete()
        return redirect("comisers")

    return render(request, "comiser/delete_comiser.html", {"obj": stud})

