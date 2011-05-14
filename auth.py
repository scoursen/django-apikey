from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import *
from key.models import ApiKey

class ApiKeyAuthentication( object ):
    def is_authenticated( self, request ):
        auth_header = getattr( settings, 'APIKEY_AUTHORIZATION_HEADER',
                               'Authorization' )
        auth_header = 'HTTP_%s' % ( auth_header.upper( ).replace( '-', '_' ) )
        auth_string = request.META.get( auth_header )
        if not auth_string:
            return False
        try:
            key = ApiKey.objects.get(key=auth_string)
            request.user = key.user
            return True
        except:
            request.user = AnonymousUser( )
            return False
        
    def challenge( self ):
        resp = HttpResponse( 'Authorization Required' )
        resp['WWW-Authenticate'] = 'KeyBasedAuthentication realm="API"'       
        auth_header = getattr( settings, 'APIKEY_AUTHORIZATION_HEADER',
                               None )
        if auth_header:
            resp[auth_header] = 'Key Needed'
        resp.status_code = 401
        return resp
