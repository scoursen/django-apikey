from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from datetime import datetime
from django.db.utils import IntegrityError
import logging
import time
import hashlib

try:
    MAX_KEYS = settings.API_MAX_KEYS
except:
    MAX_KEYS = -1

try:
    KEY_SIZE = settings.API_KEY_SIZE
except:
    KEY_SIZE = 32

class ApiKeyProfile(models.Model):
    user = models.OneToOneField(User, related_name='key_profile')
    max_keys = models.IntegerField(default=MAX_KEYS)
    last_access = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        app_label = 'key'

    def available_keys(self):
        if self.max_keys == -1:
            return 'Unlimited'
        return self.max_keys - self.api_keys.count()

    def can_make_api_key(self):
        if self.available_keys() > 0:
            return True

    def __unicode__(self):
        return "ApiKeyProfile: %s, %s" % (self.api_keys.count(),
                                          self.max_keys)

class ApiKey(models.Model):
    profile = models.ForeignKey(ApiKeyProfile, related_name='api_keys')
    key = models.CharField(max_length=KEY_SIZE, unique=True, blank=True, default='')
    logged_ip = models.CharField(max_length=32, blank=True, null=True, default=None)
    last_used = models.DateTimeField(default=datetime.utcnow)
    created = models.DateTimeField(default=datetime.utcnow)
    
    class Meta:
        app_label = 'key'
        ordering = ['-created']

    def login(self, ip_address):
        self.logged_ip = ip_address
        self.save()

    def logout(self):
        self.logged_ip = None
        self.save()
            
    def __unicode__(self):
        return 'ApiKey: %s' % (self.key)

def create_group():
    gr, cr = Group.objects.get_or_create(name='API User')
    if cr:
        ct = ContentType.objects.get(app_label="key", model="apikey")
        p, pc = Permission.objects.get_or_create(name="Can generate an API key",
                                                 codename="can_make_api_key",
                                                 content_type=ct)
        gr.permissions.add(p)
        p.save()
        p, pc = Permission.objects.get_or_create(name="Has an API key profile",
                                                 codename="has_api_key_profile",
                                                 content_type=ct)
        gr.permissions.add(p)
        p.save()
        for permission in [ 'add_apikey', 'change_apikey', 'delete_apikey' ]:
                p = Permission.objects.get(codename=permission)
                gr.permissions.add(p)
        p = Permission.objects.get(codename='change_apikeyprofile')
        gr.permissions.add(p)
        gr.save()
    return gr
