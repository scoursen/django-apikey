from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
from datetime import datetime

try:
    KEY_SIZE = settings.API_KEY_SIZE
except:
    KEY_SIZE = 16

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
        return self.max_keys - self.keys.count()

    def can_make_api_key(self):
        if self.available_keys() > 0:
            return True

    def __unicode__(self):
        return "ApiKeyProfile: %s, %s" % (self.keys.count(),
                                          self.max_keys)

class ApiKey(models.Model):
    user = models.ForeignKey(User, related_name='keys')
    key = models.CharField(max_length=KEY_SIZE, unique=True)
    logged_ip = models.IPAddressField(null=True)
    last_used = models.DateTimeField(default=datetime.utcnow)
    def login(self, ip_address):
        self.logged_ip = ip_address
        self.save()

    def logout(self):
        self.logged_ip = None
        self.save()
            
    def __unicode__(self):
        return self.key

def generate_unique_api_key(user):
    key = User.objects.make_random_password(length=KEY_SIZE)
    while ApiKey.objects.filter(key__exact=key).count():
        key = User.objects.make_random_password(length=KEY_SIZE)
    k = ApiKey(user=user, key=key)
    k.save()
    return k

admin.site.register(ApiKey)
admin.site.register(ApiKeyProfile)
