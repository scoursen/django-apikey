from django.db import models
from djangotoolbox import fields
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
from datetime import datetime
import collections
import logging
import pickle

try:
    key_size = settings.API_KEY_SIZE
except:
    key_size = 16

class ApiKey( models.Model ):
    user = models.ForeignKey( User, related_name='keys' )
    key = models.CharField( max_length=key_size, unique=True )
    logged_ip = models.IPAddressField( null=True )
    last_used = models.DateTimeField( default=datetime.utcnow )
    def __unicode__( self ):
        return self.key

def generate_unique_api_key( user ):
    key = User.objects.make_random_password( length=key_size )
    while ApiKey.objects.filter( key__exact=key ).count( ):
        key = User.objects.make_random_password( length=ks )
    k = ApiKey( user = user, key=key )
    k.save( )
    return k
        
if User.objects.filter( username='nqdq_system' ):
    if not User.objects.get( username='nqdq_system' ).keys.all( ):
        u = User.objects.get( username='nqdq_system' )
        logging.info( 'Generating API key for nqdq_system' )
        k = generate_unique_api_key( u )
        u.save( )
    else:
        logging.info( 'Not generating API key' )

admin.site.register( ApiKey )
