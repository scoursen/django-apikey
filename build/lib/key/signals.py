from django.db.models.signals import post_save
from django.db.models.signals import post_delete
import key.models


def save_api_key( sender, instance, created, **kwargs ):
    try:
        instance.user.get_profile( ).save( )
    except:
        pass
post_save.connect(save_api_key, sender=key.models.ApiKey)


def post_save_api_key( sender, instance, **kwargs ):
    try:
        instance.user.get_profile( ).save( )
    except:
        pass
post_delete.connect(post_save_api_key, sender=key.models.ApiKey)
