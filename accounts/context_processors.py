# from .models import SystemStatus

# def system_status(request):
#     system_status = SystemStatus.objects.first()

#     return {
#         "system_closed": system_status.is_system_closed() if system_status else False,
#         "closure_time": system_status.closure_start if system_status and system_status.closure_start else None,
#         "closure_end": system_status.closure_end if system_status and system_status.closure_end else None,
#     }