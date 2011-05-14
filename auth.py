from django.http import HttpResponse
from django.contrib.auth.models import *
from key.models import ApiKey
import logging

class ApiKeyAuthentication( object ):
    def is_authenticated( self, request ):
        auth_string = request.META.get( 'HTTP_AUTHORIZATION' )
        if not auth_string:
            return False
        try:
            key = ApiKey.objects.get( key=auth_string )
            request.user = key.user
            return True
        except:
            raise
            request.user = AnonymousUser( )
            return False

    def challenge( self ):
        resp = HttpResponse( 'Authorization Required' )
        resp['WWW-Authenticate'] = 'KeyBasedAuthentication realm="API"'
        resp.status_code = 401
        return resp
