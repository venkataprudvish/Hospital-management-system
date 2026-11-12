from django.conf import settings

def security_context(request):
    return {"APP_NAME": "SecureCare HMS", "DEBUG_MODE": settings.DEBUG}
