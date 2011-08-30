from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import *
from django.views.generic.base import TemplateResponseMixin, View
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition, last_modified
from django.views.decorators.cache import cache_control, cache_page
from django.core.urlresolvers import reverse
from django.core.cache import cache
from key.models import ApiKey, generate_unique_api_key
from key.forms import *
from django.contrib.auth.models import User
import hashlib
import datetime
import logging
import decorator

def get_etag_key(request):
    try:
        lm = request.user.key_profile.last_access
    except:
        lm = datetime.datetime.utcnow()
    k = 'etag.%s.%s.%s' % (lm, request.path, request.user)
    k = k.replace(' ', '_')
    return hashlib.md5(k).hexdigest()

def etag_func(request, *args, **kwargs):
    etag_key = get_etag_key(request)
    etag = cache.get(etag_key, None)
    return etag

def latest_access(request, *args, **kwargs):
    try:
        return request.user.key_profile.last_access
    except:
        return datetime.datetime.utcnow()

class ProtectedView(object):
    @method_decorator(permission_required('key.has_api_key_profile'))
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProtectedView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

if 'django.middleware.cache.UpdateCacheMiddleware' in settings.MIDDLEWARE_CLASSES:
    from django import utils
    class CachedView(object):
        @method_decorator(cache_page(1))
        @method_decorator(condition(etag_func=etag_func, last_modified_func=latest_access))
        def get(self, request, *args, **kwargs):
            import rfc822
            import time            
            rv = super(CachedView, self).get(request, *args, **kwargs)
            if not request.user.is_anonymous():
                utils.cache.patch_cache_control(rv, private=True)
            etag = get_etag_key(request)
            if etag:
                rv['ETag'] = etag
            return rv
else:
    class CachedView(object):
        pass

class KeyCreateView(ProtectedView, CreateView):
    def get_success_url(self):
        return reverse('key.list')

    def post(self, request, *args, **kwargs):
        self.object = generate_unique_api_key(self.request.user)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
    
        
class KeyListView(CachedView, ProtectedView, ListView):
    def get_queryset(self):
        profile = self.request.user.key_profile
        return ApiKey.objects.filter(profile=profile)

    def get_context_data(self, **kwargs):
        context = super(KeyListView, self).get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['can_make_api_key'] = user.key_profile.can_make_api_key()
        context['available_keys'] = user.key_profile.available_keys()
        return context

class KeyDeleteView(ProtectedView, DeleteView):
    def get_success_url(self):
        return reverse('key.list')

    def get_object(self):
        return self.get_queryset().get(key=self.kwargs['key_code'])

    def get_queryset(self):
        profile = self.request.user.key_profile
        return profile.api_keys.all()

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('action') == 'Cancel':
            return HttpResponseRedirect(self.get_success_url())
        return super(KeyDeleteView, self).post(request, *args, **kwargs)

