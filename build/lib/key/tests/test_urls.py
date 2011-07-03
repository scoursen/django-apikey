from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from piston.resource import Resource
from piston.handler import BaseHandler, AnonymousBaseHandler
from key.auth import *
import key.urls

class KeyHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ApiKey
    
    def read(self, request):
        try:
            return ApiKey.objects.filter(user=request.user)
        except AccessForbidden:
            return rc.FORBIDDEN
        except ApiKey.DoesNotExist:
            return rc.NOT_FOUND
        except self.model.DoesNotExist:
            return rc.NOT_FOUND


auth = ApiKeyAuthentication()
key_handler = Resource(handler=KeyHandler,
                       authentication=auth)


test_patterns = patterns('',                       
                         url(r'^k/$', key_handler, name="test_key_list" ),
                         )

key.urls.urlpatterns = key.urls.urlpatterns + test_patterns
