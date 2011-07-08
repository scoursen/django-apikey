from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from piston.resource import Resource
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import *
from key.auth import *
import key.urls

class KeyHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ApiKey
    
    def read(self, request):
        return ApiKey.objects.filter(profile=request.user.key_profile)
        

class KeyViewHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = ApiKey

    def read(self, request, key_pk):
        try:
            return ApiKey.objects.get(profile=request.user.key_profile,
                                      pk=key_pk)
        except self.model.DoesNotExist:
            return rc.NOT_FOUND

auth = ApiKeyAuthentication()
key_handler = Resource(handler=KeyHandler,
                       authentication=auth)
key_view_handler = Resource(handler=KeyViewHandler,
                            authentication=auth)

test_patterns = patterns('',                       
                         url(r'^k/$', key_handler, name="test_key_list" ),
                         url(r'^k/(?P<key_pk>\d+?)$', key_view_handler, name="test_key_view"),
                         )

key.urls.urlpatterns = key.urls.urlpatterns + test_patterns
