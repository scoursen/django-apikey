from django.contrib.auth.models import User, Permission, user_logged_in
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from key.models import *
from key.signals import *
import logging
import time
import hashlib

def perm_check(user):
    try:
        if user.key_profile:
            return
    except:
        if user.has_perm("key.has_api_key_profile"):
            if user.groups.filter(name='API User').count():
                profile, created = ApiKeyProfile.objects.get_or_create(user=user)
                if created:
                    api_user_created.send(sender=user.__class__,
                                          instance=user)
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

def generate_unique_key_code(user, key):
    perm_check(user)
    while True:
        now = datetime.utcnow()
        kstr = hashlib.md5('%s-%s' % (user.email, now)).hexdigest()[:KEY_SIZE]
        if key:
            key.key = kstr
            key.created = now
            try:
                key.save()
                return key
            except IntegrityError:
                time.sleep(0.01)
        else:
            key, created = ApiKey.objects.get_or_create(profile=user.key_profile,
                                                        key=kstr,
                                                        created=now)
            if not created:
                time.sleep(0.01)
            else:
                return key

def generate_unique_api_key(user,key_object=None):
    perm_check(user)
    if not key_object:
        key = None
    else:
        key = key_object
    key = generate_unique_key_code(user, key)
    return key

def update_profile_timestamps(sender, instance, created, *args, **kwargs):
    instance.profile.last_accessed = datetime.utcnow()
    instance.profile.save()
post_save.connect(update_profile_timestamps, sender=ApiKey, dispatch_uid='update_profile_timstamps')


