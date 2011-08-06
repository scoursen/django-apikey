from django.test import TestCase, Client
from django.contrib.auth.models import User, user_logged_in
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models.signals import post_save
from key.models import ApiKey, ApiKeyProfile, generate_unique_api_key, MAX_KEYS
import hashlib
import test_urls

class ApiKeyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='ApiKeyTest',
                                        email='ApiKeyTest@t.com')
        self.user.set_password('ApiKeyTestPassword')
        self.user.save()
        generate_unique_api_key(self.user)

    def test_key_profile(self):
        profile = self.user.key_profile
        self.assertNotEquals(profile, None)
        self.assertEquals(profile.user, self.user)
        self.assertEquals(profile.max_keys, MAX_KEYS)
        self.profile_signaled = False
        def check_signal(sender, instance, created, *args, **kwargs):
            self.profile_signaled = True
        post_save.connect(check_signal, sender=ApiKeyProfile,
                          dispatch_uid='test_check_signal')
        k = profile.api_keys.all()[0]
        k.save()
        self.assertTrue(self.profile_signaled)

    def test_key_generation(self):
        k = generate_unique_api_key(self.user)
        my_kstr = hashlib.md5('%s-%s' % (self.user.email,
                                         k.created)).hexdigest()[:settings.API_KEY_SIZE]
        self.assertTrue(self.user.key_profile.can_make_api_key())
        self.assertEquals(self.user.key_profile.available_keys(), 'Unlimited')
        self.assertEquals(my_kstr, k.key)
        self.assertEquals(self.user.key_profile.api_keys.count(), 2)
        k.delete()
        self.assertEquals(self.user.key_profile.api_keys.count(), 1)        
        current_max = self.user.key_profile.max_keys
        self.user.key_profile.max_keys = 2
        self.user.key_profile.save()
        self.assertEquals(self.user.key_profile.max_keys, 2)
        self.assertEquals(self.user.key_profile.available_keys(), 1)
        self.assertTrue(self.user.key_profile.can_make_api_key())
        self.user.key_profile.max_keys = 1
        self.user.key_profile.save()
        self.assertEquals(self.user.key_profile.max_keys, 1)
        self.assertEquals(self.user.key_profile.available_keys(), 0)
        self.assertFalse(self.user.key_profile.can_make_api_key())
        self.user.key_profile.max_keys = current_max
        self.user.key_profile.save()
        k = self.user.key_profile.api_keys.all()[0]
        self.assertEquals(self.user.key_profile.__unicode__(), 'ApiKeyProfile: 1, %s' % current_max)
        self.assertEquals(k.__unicode__(), 'ApiKey: %s' % k.key)

    def test_authentication(self):
        def do_test_authentication(auth_header):
            client = Client()
            def t_user_logged_in(*args, **kwargs):
                self.user_signalled = True
            auth_header = 'HTTP_%s' % (auth_header.upper().replace('-', '_'))
            key = self.user.key_profile.api_keys.all()[0]
            extra = {auth_header: key.key}
        
            self.user_signalled = False
            user_logged_in.connect(t_user_logged_in, dispatch_uid='t_user_logged_in')
            
            rv = client.get(reverse('test_key_list'), **extra)
            self.assertEquals(rv.status_code, 200)
            key.login('127.0.0.1')
            self.assertEquals(key.logged_ip, '127.0.0.1')
            self.assertTrue(self.user_signalled)
            
            rv = client.get(reverse('test_key_view', args=(key.pk,)))
            self.assertEquals(rv.status_code,401)
            rv = client.get(reverse('test_key_view', args=(key.pk,)), **extra)
            self.assertEquals(rv.status_code,200)
            rv = client.get(reverse('test_key_view', args=(key.pk+1,)), **extra)
            self.assertEquals(rv.status_code, 404)
            
            rv = client.get(reverse('test_key_list'))
            self.assertEquals(rv.status_code, 401)
            self.user.key_profile.api_keys.all()[0].logout()
            key.logout()
            self.assertEquals(key.logged_ip, None)
        do_test_authentication('X-Api-Authorization')
        settings.APIKEY_AUTHORIZATION_HEADER = 'X-MyCoolApp-Key'
        do_test_authentication('X-MyCoolApp-Key')

    def test_views(self):
        client = Client()
        rv = client.get(reverse('api_key_list'))
        self.assertEquals(rv.status_code, 302)
        rv = client.get(reverse('api_key_create'))
        self.assertEquals(rv.status_code, 302)
        rv = client.get(reverse('api_key_delete',args=('ValueDoesntMatter',)))
        self.assertEquals(rv.status_code, 302)
        client = Client()
        client.login(username='ApiKeyTest',
                     password='ApiKeyTestPassword')
        rv = client.get(reverse('api_key_list'))
        self.assertEquals(rv.status_code, 200)
        original_list = list(self.user.key_profile.api_keys.all())
        self.assertEquals(self.user.key_profile.api_keys.count(), 1)
        rv = client.post(reverse('api_key_create'))
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(self.user.key_profile.api_keys.count(), 2)
        k = self.user.key_profile.api_keys.all()[0]
        self.assertTrue(k not in original_list)
        rv = client.post(reverse('api_key_delete',args=(k.key,)))
        self.assertTrue(k not in self.user.key_profile.api_keys.all())
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(self.user.key_profile.api_keys.count(), 1)
        
