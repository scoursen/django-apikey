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

try:
    USE_API_GROUP = settings.USE_API_GROUP
except:
    USE_API_GROUP = None

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

def assign_permissions(user_or_group):
    ct = ContentType.objects.get(app_label="key", model="apikey")
    can_gen, pc = Permission.objects.get_or_create(name="Can generate an API key",
                                             codename="can_make_api_key",
                                             content_type=ct)
    ct = ContentType.objects.get(app_label='key', model='apikeyprofile')
    has_prof, pc = Permission.objects.get_or_create(name="Has an API key profile",
                                             codename="has_api_key_profile",
                                             content_type=ct)
    can_login, pc = Permission.objects.get_or_create(name="Can use the API",
                                                     codename="can_use_api",
                                                     content_type=ct)
    perm_list = getattr(user_or_group, 'permissions', 
                        getattr(user_or_group, 'user_permissions'))
    perm_list.add(can_gen)
    perm_list.add(has_prof)
    perm_list.add(can_login)
    for permission in [ 'add_apikey', 'change_apikey', 'delete_apikey' ]:
        p = Permission.objects.get(codename=permission)
        perm_list.add(p)
    p = Permission.objects.get(codename='change_apikeyprofile')
    perm_list.add(p)
    user_or_group.save()
    return user_or_group
    
def create_group():
    if USE_API_GROUP:
        gr, cr = Group.objects.get_or_create(name='API User')
        if cr:
            assign_permissions(gr)
        return gr
