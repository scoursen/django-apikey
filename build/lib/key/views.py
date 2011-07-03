from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import condition, last_modified
from django.views.decorators.cache import cache_control, cache_page
from django.core.cache import cache
from key.models import ApiKey, generate_unique_api_key
from django.contrib.auth.models import User
import datetime
import logging


def get_etag_key(request):
    try:
        lm = request.user.get_profile().last_accessed
    except:
        try:
            lm = request.get_profile().last_accessed
        except:
            lm = datetime.datetime.utcnow()
    k = 'etag.%s' % (lm)
    return k.replace(' ', '_')

def etag_func(request, *args, **kwargs):
    etag_key = get_etag_key(request)
    etag = cache.get(etag_key, None)
    return etag

def latest_access(request, *args, **kwargs):
    try:
        return request.user.get_profile().last_accessed
    except:
        return datetime.datetime.utcnow()



@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def generate_key(request):
    if request.method == 'POST':
        key = generate_unique_api_key(request.user)
    return do_generate_key_list(request)


@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def list_keys(request):
    return do_generate_key_list(request)

def do_generate_key_list(request):
    keys = ApiKey.objects.filter(user=request.user)
    user = request.user
    cmak = user.key_profile.can_make_api_key()
    ak = user.key_profile.available_keys()
    return render_to_response('key/key.html',
                              { 'keys': keys, 'user': user,
                                'can_make_api_key': cmak,
                                'available_keys': ak },
                              context_instance=RequestContext(request))

@login_required
@condition(etag_func=etag_func, last_modified_func=latest_access)
@cache_page(1)
def delete_key(request, key):
    key = get_object_or_404(ApiKey, key=key)
    key.delete()
    return do_generate_key_list(request)

