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
            profile, created = ApiKeyProfile.objects.get_or_create(user=user)
            if created:
                api_user_created.send(sender=user.__class__,
                                      instance=user)
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

def generate_unique_key_code(user):
    perm_check(user)
    while True:
        now = datetime.utcnow()
        kstr = hashlib.md5('%s-%s' % (user.email, now)).hexdigest()[:KEY_SIZE]
        key, created = ApiKey.objects.get_or_create(profile=user.key_profile,
                                                    key=kstr,
                                                    created=now)
        if created:
            try:
                key.save()
                return key
            except IntegriyError:
                pass
        time.sleep(0.01)

def generate_unique_api_key(user):
    key = generate_unique_key_code(user)
    api_key_created.send(sender=key.__class__, instance=key)
    return key

def update_profile_timestamps(sender, instance, created, *args, **kwargs):
    instance.profile.last_access = datetime.utcnow()
    instance.profile.save()
post_save.connect(update_profile_timestamps, sender=ApiKey, dispatch_uid='update_profile_timstamps')

def send_login_logout_signals(sender, instance, created, *args, **kwargs):
    if instance.logged_ip:
        api_user_logged_in.send(sender=instance.profile.user.__class__,
                                user=instance.profile.user)
    else:
        api_user_logged_out.send(sender=instance.profile.user.__class__,
                                 user=instance.profile.user)
post_save.connect(send_login_logout_signals, sender=ApiKey, dispatch_uid='send_loging_logout_signals')

def create_key_profile(user):
    profile, c = ApiKeyProfile.objects.get_or_create(user=user)
    if c:
        api_user_created.send(sender=user.__class__,
                              instance=user)
    return profile

def create_key_profile_signal(sender, instance, created, *args, **kwargs):
    if created:
        create_key_profile(instance)
