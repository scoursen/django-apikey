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

class ApiKeyProfile(models.Model):
    user = models.OneToOneField(User, related_name='key_profile')
    max_keys = models.IntegerField(default=MAX_KEYS)

    def available_keys(self):
        if self.max_keys == -1:
            return 'Unlimited'
        return self.max_keys - self.api_keys.count()

    def can_make_api_key(self):
        if self.available_keys() > 0:
            return True

    def __unicode__(self):
        return "ApiKeyProfile: %s, %s" % (self.keys.count(),
                                          self.max_keys)

class ApiKey(models.Model):
    profile = models.ForeignKey(ApiKeyProfile, related_name='api_keys')
    key = models.CharField(max_length=32, unique=True)
    logged_ip = models.IPAddressField(null=True)
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
        return self.key

def generate_unique_api_key(user):
    while True:
        now = datetime.utcnow()
        key = ApiKey(profile=user.key_profile,created=now)
        kstr = hashlib.md5('%s-%s' % (user.email, now)).hexdigest()
        key.key = kstr
        try:
            key.save()
            return key
        except IntegrityError:
            time.sleep(0.01)

def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        profile, profile_created = ApiKeyProfile.objects.get_or_create(user=instance)
        if profile_created:
            profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid='create_profile')
admin.site.register(ApiKey)
admin.site.register(ApiKeyProfile)

