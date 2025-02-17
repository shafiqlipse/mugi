from django.shortcuts import render
from django.http import HttpResponseServerError

class ServiceUnavailableMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Example: Enable 503 maintenance mode based on a flag
        maintenance_mode = False  # Change to True when needed
        
        if maintenance_mode:
            return render(request, '503.html', status=503)
        
        return self.get_response(request)
