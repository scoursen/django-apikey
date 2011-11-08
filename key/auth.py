from django.http import HttpResponse
from django.core import cache
from django.contrib.auth.models import *
from key.models import ApiKey
from key import settings
import logging
import hashlib

def _key_cache_key(auth_string):
    kstr = 'key.%s' % auth_string
    return hashlib.md5(kstr).hexdigest()

class ApiKeyAuthentication(object):
    def is_authenticated(self, request):
        auth_header = getattr(settings, 'AUTH_HEADER')
        auth_header = 'HTTP_%s' % (auth_header.upper().replace('-', '_'))
        auth_string = request.META.get(auth_header)
        if not auth_string:
            return False
        try:
            user = cache.get_cache('default').get(_key_cache_key(auth_string))
            if user:
                request.user = user
            else:
                key = ApiKey.objects.get(key=auth_string)
                key.login(request.META.get('REMOTE_ADDR'))
                request.user = key.profile.user
                cache.get_cache('default').set(_key_cache_key(key.key), request.user)
                if not key.profile.user.has_perm('key.can_use_api'):
                    return False                
                user_logged_in.send(sender=request.user.__class__,
                                    request=request, user=request.user)
                
        except ApiKey.DoesNotExist:
            return False
        request.key = auth_string
        return True
        
    def challenge(self):
        auth_header = getattr(settings, 'AUTH_HEADER')
        resp = HttpResponse('Authorization Required')
        resp['WWW-Authenticate'] = 'KeyBasedAuthentication realm="API"'       
        resp[auth_header] = 'Key Needed'
        resp.status_code = 401
        return resp
