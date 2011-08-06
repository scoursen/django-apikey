from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
from datetime import datetime
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.db.utils import IntegrityError
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
    key = models.CharField(max_length=KEY_SIZE, unique=True, blank=True, default=None)
    logged_ip = models.CharField(max_length=32, null=True, blank=True, default=None)
    last_used = models.DateTimeField(default=datetime.utcnow)
    created = models.DateTimeField(default=datetime.utcnow)
    
    class Meta:
        ordering = ['-created']

    def login(self, ip_address):
        self.logged_ip = ip_address
        self.save()

    def logout(self):
        self.logged_ip = None
        self.save()
            
    def __unicode__(self):
        return 'ApiKey: %s' % (self.key)

def generate_unique_key_code(user, key):
    while True:
        now = datetime.utcnow()
        key.created = now
        kstr = hashlib.md5('%s-%s' % (user.email, now)).hexdigest()[:KEY_SIZE]
        key.key = kstr
        try:
            key.save()
            return key
        except IntegrityError:
            time.sleep(0.01)

def generate_unique_api_key(user,key_object=None):
    if not key_object:
        key = ApiKey(profile=user.key_profile)
    else:
        key = key_object
    key = generate_unique_key_code(user, key)
    return key

def create_profile(sender, instance, created, *args, **kwargs):
    try:
        if created or instance.key_profile is None:
            profile, profile_created = ApiKeyProfile.objects.get_or_create(user=instance)
            if profile_created:
                profile.save()
    except:
        #We can fail during syncdb when using South
        pass

post_save.connect(create_profile, sender=User, dispatch_uid='create_profile')

def update_profile_timestamps(sender, instance, created, *args, **kwargs):
    instance.profile.last_accessed = datetime.utcnow()
    instance.profile.save()

post_save.connect(update_profile_timestamps, sender=ApiKey, dispatch_uid='update_profile_timstamps')


