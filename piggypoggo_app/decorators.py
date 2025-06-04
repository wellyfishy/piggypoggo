from django.http import HttpResponseForbidden
from functools import wraps

def status_required(allowed_statuses):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_profile = getattr(request.user, 'userprofile', None)
            if not user_profile or user_profile.level not in allowed_statuses:
                return HttpResponseForbidden("Unauthorized")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator