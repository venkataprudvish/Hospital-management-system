# Security model

## Trust boundaries

1. Browser -> Django: all authorization decisions are server-side.
2. Django -> database: ORM access with explicit query scoping.
3. Public internet -> application: HTTPS, security headers, CSRF, abuse throttling.
4. Admin -> privileged data: Django staff/superuser controls.

## Key controls

- Least-privilege registration: self-registration creates a Patient account.
- Elevated roles are not selectable during public registration.
- Patient, doctor, appointment, and billing queries are scoped by the authenticated user's role/relationship.
- POST actions require CSRF tokens and server-side permission checks.
- Login and registration have basic IP-based abuse throttling and return HTTP 429 after the configured threshold.
- Secrets and database URLs come from environment variables in production.
- `DEBUG=False` is required for production security settings.
- Secure cookies and HSTS are enabled when `DEBUG=False`.
- A restrictive Content-Security-Policy is applied to the public application; Django admin is excluded to preserve its own assets.

## Limitations

The built-in abuse limiter uses Django's cache. For a multi-worker or multi-instance deployment, use a shared production cache (for example Redis) or a dedicated reverse-proxy/WAF rate limiter.

This project is a student/demo HMS. Do not use it for real patient data until it has undergone a formal security, privacy, compliance, backup, incident-response, and infrastructure review.
