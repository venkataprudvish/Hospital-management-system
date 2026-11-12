from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security-related HTTP response headers.

    These headers are applied to the public application.
    Django Admin is excluded from the restrictive CSP because
    Django Admin has its own JavaScript/CSS requirements.
    """

    def process_response(self, request, response):
        response["X-Content-Type-Options"] = "nosniff"

        response["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )

        response["Permissions-Policy"] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        response["X-Frame-Options"] = "DENY"

        # HSTS should only be sent when the application is
        # actually running in production over HTTPS.
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = (
                "max-age=31536000; "
                "includeSubDomains"
            )

        # Django Admin has its own assets and JavaScript.
        # Keep the restrictive CSP for the public application.
        if not request.path.startswith("/admin/"):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "style-src 'self'; "
                "script-src 'self'; "
                "connect-src 'self'"
            )

        return response


class AbuseRateLimitMiddleware(MiddlewareMixin):
    """
    Basic application-level rate limiting for sensitive POST endpoints.

    Limits are intentionally kept small for authentication-related
    endpoints to reduce automated abuse.

    NOTE:
    The current cache backend is suitable for local/single-process
    development. A shared cache should be used for multi-worker
    production deployments.
    """

    LIMITS = {
        "/login/": (5, 300),
        "/register/": (10, 3600),
    }

    def process_request(self, request):
        # Only rate-limit state-changing POST requests.
        if request.method != "POST":
            return None

        rule = self.LIMITS.get(request.path)

        if rule is None:
            return None

        limit, window = rule

        ip_address = request.META.get(
            "REMOTE_ADDR",
            "unknown",
        ).strip()

        if not ip_address:
            ip_address = "unknown"

        cache_key = (
            f"abuse:{request.path}:{ip_address}"
        )

        current_count = cache.get(cache_key, 0)

        if current_count >= limit:
            response = HttpResponse(
                "Too many requests. Please try again later.",
                status=429,
                content_type="text/plain",
            )

            response["Retry-After"] = str(window)
            response["Cache-Control"] = "no-store"

            return response

        cache.set(
            cache_key,
            current_count + 1,
            timeout=window,
        )

        return None