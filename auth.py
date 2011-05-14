from django.http import HttpResponse
from django.contrib.auth.models import *
from key.models import ApiKey
import logging

class ApiKeyAuthentication( object ):
    def is_authenticated( self, request ):
        logging.error("fff")
        auth_string = request.META.get( 'HTTP_AUTHORIZATION' )
        logging.error("auth_string %s" % auth_string)
        if not auth_string:
            return False
        try:
            key = ApiKey.objects.get(key=auth_string)
            logging.error("key: %s" % key)
            request.user = key.user
            return True
        except:
            request.user = AnonymousUser( )
            return False

    def challenge( self ):
        resp = HttpResponse( 'Authorization Required' )
        resp['WWW-Authenticate'] = 'KeyBasedAuthentication realm="API"'
        resp.status_code = 401
        return resp
