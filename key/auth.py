from django.http import HttpResponse
from django.contrib.auth.models import *
from key.models import ApiKey
from key import settings
import logging

class ApiKeyAuthentication(object):
    def is_authenticated(self, request):
        auth_header = getattr(settings, 'AUTH_HEADER')
        auth_header = 'HTTP_%s' % (auth_header.upper().replace('-', '_'))
        auth_string = request.META.get(auth_header)
        if not auth_string:
            return False
        try:
            key = ApiKey.objects.get(key=auth_string)
        except ApiKey.DoesNotExist:
            return False
        key.login(request.META.get('REMOTE_ADDR'))
        if not key.profile.user.has_perm('key.can_use_api'):
            return False
        request.user = key.profile.user
        user_logged_in.send(sender=key.profile.user.__class__,
                            request=request, user=key.profile.user)
        return True
        
    def challenge(self):
        auth_header = getattr(settings, 'AUTH_HEADER')
        resp = HttpResponse('Authorization Required')
        resp['WWW-Authenticate'] = 'KeyBasedAuthentication realm="API"'       
        resp[auth_header] = 'Key Needed'
        resp.status_code = 401
        return resp
