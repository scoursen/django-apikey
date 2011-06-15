from django.conf.urls.defaults import *


urlpatterns = patterns('key.views',
                       url(r'^create_key/$', 'generate_key', 
                           name='api_create_key' ),
                       url(r'^keys/$', 'list_keys',
                           name='api_list_keys' ),
                       url(r'^delete_key/$', 'delete_key',
                           name='api_delete_key' ),
                       )
