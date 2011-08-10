from django.conf.urls.defaults import *
from key.views import *

urlpatterns = patterns('key.views',
                       url(r'^create_key/$', KeyCreateView.as_view(),
                           name='api_key_create' ),
                       url(r'^keys/$', KeyListView.as_view(),
                           name='api_key_list' ),
                       url(r'^delete_key/(?P<key_code>.*)/$', 
                           KeyDeleteView.as_view(),
                           name='api_key_delete' ),
                       )
