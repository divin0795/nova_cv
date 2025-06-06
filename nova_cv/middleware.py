# nova_cv/middleware.py
from django.utils.deprecation import MiddlewareMixin

class LogHostHeaderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"Host header: {request.META.get('HTTP_HOST')}")
        print(f"X-Forwarded-Proto: {request.META.get('HTTP_X_FORWARDED_PROTO')}")
