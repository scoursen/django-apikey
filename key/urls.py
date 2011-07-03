from django.conf.urls.defaults import *


urlpatterns = patterns('key.views',
                       url(r'^create_key/$', 'generate_key', 
                           name='api_key_create' ),
                       url(r'^keys/$', 'list_keys',
                           name='api_key_list' ),
                       url(r'^delete_key/(?P<key>.*)/$', 'delete_key',
                           name='api_key_delete' ),
                       )
