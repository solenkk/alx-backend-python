import logging
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, time
from django.conf import settings

class RequestLoggingMiddleware:
    """Middleware to log all incoming requests"""
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = self._configure_logger()

    def _configure_logger(self):
        """Configure request logging settings"""
        logger = logging.getLogger('request_logger')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('requests.log')
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        logger.addHandler(handler)
        return logger

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path} - Method: {request.method}"
        self.logger.info(log_message)
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    """Middleware to restrict chat access during certain hours"""
    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_start = getattr(settings, 'RESTRICTED_START', time(21, 0))  # 9 PM default
        self.restricted_end = getattr(settings, 'RESTRICTED_END', time(6, 0))       # 6 AM default
        self.restricted_paths = getattr(settings, 'RESTRICTED_PATHS', ['/chat/', '/messages/', '/api/chat/'])

    def __call__(self, request):
        current_time = datetime.now().time()
        is_restricted = ((current_time >= self.restricted_start) or 
                        (current_time <= self.restricted_end))
        
        if (is_restricted and 
            any(request.path.startswith(p) for p in self.restricted_paths) and 
            not getattr(request.user, 'is_staff', False)):
            return JsonResponse(
                {
                    "error": "Chat access is restricted between 9 PM and 6 AM",
                    "status": 403
                },
                status=403
            )
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    """Middleware to rate limit message sending"""
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('rate_limit')
        self.limit = getattr(settings, 'RATE_LIMIT', 5)  # 5 messages default
        self.window = getattr(settings, 'TIME_WINDOW', 60)  # 60 seconds default
        self.protected_paths = getattr(settings, 'MESSAGE_PATHS', ['/api/messages/', '/chat/send/'])

    def __call__(self, request):
        if (request.method == 'POST' and 
            any(request.path.startswith(p) for p in self.protected_paths)):
            
            ip = self._get_client_ip(request)
            cache_key = f"rl_{ip}"
            count = cache.get(cache_key, 0)
            
            if count >= self.limit:
                self.logger.warning(f"Rate limit exceeded for {ip}")
                return JsonResponse(
                    {
                        "error": "Too many messages. Please wait.",
                        "status": 429
                    },
                    status=429
                )
            
            cache.set(cache_key, count + 1, self.window)
        
        return self.get_response(request)

    def _get_client_ip(self, request):
        """Extract client IP from request"""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0] if xff else request.META.get('REMOTE_ADDR')

class RolepermissionMiddleware:
    """Middleware to enforce role-based permissions"""
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_paths = getattr(settings, 'ADMIN_PATHS', [
            '/admin/', '/api/admin/', '/chat/delete/'
        ])
        self.moderator_paths = getattr(settings, 'MODERATOR_PATHS', [
            '/api/moderate/', '/chat/edit/'
        ])

    def __call__(self, request):
        needs_admin = any(request.path.startswith(p) for p in self.admin_paths)
        needs_mod = any(request.path.startswith(p) for p in self.moderator_paths)

        if needs_admin or needs_mod:
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Login required", "status": 401},
                    status=401
                )
            
            if needs_admin and not getattr(request.user, 'is_admin', False):
                return JsonResponse(
                    {"error": "Admin access required", "status": 403},
                    status=403
                )
            
            if needs_mod and not getattr(request.user, 'is_moderator', False):
                return JsonResponse(
                    {"error": "Moderator access required", "status": 403},
                    status=403
                )
        
        return self.get_response(request)
    
