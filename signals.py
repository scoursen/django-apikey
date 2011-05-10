from annoying.decorators import signals
from datetime import datetime
import key.models

@signals.post_save( sender=key.models.ApiKey )
def save_api_key( sender, instance, created, **kwargs ):
    try:
        instance.user.get_profile( ).save( )
    except:
        pass

@signals.post_delete( sender=key.models.ApiKey )
def post_save_api_key( sender, instance, **kwargs ):
    try:
        instance.user.get_profile( ).save( )
    except:
        pass

