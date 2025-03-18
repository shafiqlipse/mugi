from django.shortcuts import render

# Create your views here.
def zonalchair_list(request):
    return render(request, "zonalchair_list.html")
# Compare this snippet from usssa/zone/templates/zone/zonalchair_list.html: 



def zonalchair_create(request):
    return render(request, "zonalchair_create.html")
# Compare this snippet from usssa/zone/templates/zone/zonalchair_create.html:

def zonalchair_detail(request):
    return render(request, "zonalchair_detail.html")

def zonalchair_update(request):
    return render(request, "zonalchair_update.html")    

def zonalchair_delete(request):
    return render(request, "zonalchair_delete.html")