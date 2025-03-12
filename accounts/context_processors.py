from .models import SystemStatus

def system_status(request):
    system_status = SystemStatus.objects.first()
    closure_time = system_status.closure_start if system_status else None

    print(f"DEBUG: Closure Time → {closure_time}")  # Debugging

    return {
        "system_closed": system_status.is_system_closed() if system_status else False,
        "closure_time": closure_time
    }