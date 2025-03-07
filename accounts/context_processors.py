from .models import SystemStatus

def system_status(request):
    status = SystemStatus.objects.first()
    return {
        'system_closed': status.is_system_closed() if status else False,
        'closure_start': status.closure_start if status else None,
        'closure_end': status.closure_end if status else None,
    }
