from django.http import HttpResponse
from django.contrib.auth.models import *
from django.shortcuts import render_to_response
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

    """
    Support for usage as a regular Django authentication backend.
    You probably don't want to do this, but it's included for completeness.
    """
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user( self, user_id ):
        """user_id is really the API key"""
        try:
            key = ApiKey.objects.get( key=user_id )
            return key.user
        except Key.DoesNotExist:
            return None

    def is_authenticated( self, username=None, password=None ):
        try:
            key = ApiKey.objects.get( key=username )
            return key.user
        except Key.DoesNotExist:
            return None
