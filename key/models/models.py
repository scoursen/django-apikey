from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from datetime import datetime
from django.db.utils import IntegrityError
import logging
import time
import hashlib
from key.settings import MAX_KEYS, KEY_SIZE, USE_API_GROUP
from key.signals import api_user_logged_in

class ApiKeyProfile(models.Model):
    user = models.OneToOneField(User, related_name='key_profile')
    max_keys = models.IntegerField(default=MAX_KEYS)
    last_access = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        app_label = 'key'
        permissions = (
            ('has_api_key_profile', 'Has an API key profile'),
            ('can_use_api', 'Can use the API'),
            )

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
        permissions = (
            ('can_make_api_key', 'Can generate an API key'),
            )


    def login(self, ip_address):
        self.logged_ip = ip_address
        self.save()

    def logout(self):
        self.logged_ip = None
        self.save()

    def __unicode__(self):
        return 'ApiKey: %s' % (self.key)

def assign_api_key_permissions(user_or_group):
    perm_list = getattr(user_or_group, 'permissions',
                        getattr(user_or_group, 'user_permissions'))
    ct = ContentType.objects.get(app_label='key', model='apikeyprofile')
    hakp, _ = Permission.objects.get_or_create(codename='has_api_key_profile', content_type=ct)
    cua, _ = Permission.objects.get_or_create(codename='can_use_api', content_type=ct)
    ct = ContentType.objects.get(app_label='key', model='apikey')
    cmak, _ = Permission.objects.get_or_create(codename='can_make_api_key', content_type=ct)
    p = Permission.objects.get(codename='change_apikeyprofile')
    perm_list.add(hakp, cua, cmak, p)
    return user_or_group

def create_group():
    if USE_API_GROUP:
        gr, cr = Group.objects.get_or_create(name='API User')
        if cr:
            assign_api_key_permissions(gr)
        return gr
