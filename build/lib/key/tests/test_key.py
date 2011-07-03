from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from key.models import ApiKey, ApiKeyProfile, generate_unique_api_key
import hashlib
import test_urls

class ApiKeyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='ApiKeyTest',
                                        email='ApiKeyTest@t.com')
        self.user.set_password('ApiKeyTestPassword')
        self.user.save()
        generate_unique_api_key(self.user)

    def test_key_generation(self):
        k = generate_unique_api_key(self.user)
        my_kstr = hashlib.md5('%s-%s' % (self.user.email,
                                         k.created)).hexdigest()
        self.assertEquals(my_kstr, k.key)
        self.assertEquals(self.user.api_keys.count(), 2)
        k.delete()
        self.assertEquals(self.user.api_keys.count(), 1)        

    def test_authentication(self):
        client = Client()
        auth_header = getattr(settings, 'APIKEY_AUTHORIZATION_HEADER',
                               'X-Api-Authorization')
        auth_header = 'HTTP_%s' % (auth_header.upper().replace('-', '_'))
        extra = {auth_header: self.user.api_keys.all()[0].key}
        rv = client.get(reverse('test_key_list'), **extra)
        self.assertEquals(rv.status_code, 200)
        rv = client.get(reverse('test_key_list'))
        self.assertEquals(rv.status_code, 401)

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
        original_list = list(self.user.api_keys.all())
        self.assertEquals(self.user.api_keys.count(), 1)
        rv = client.post(reverse('api_key_create'))
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(self.user.api_keys.count(), 2)
        k = self.user.api_keys.all()[0]
        self.assertTrue(k not in original_list)
        rv = client.post(reverse('api_key_delete',args=(k.key,)))
        self.assertTrue(k not in self.user.api_keys.all())
        self.assertEquals(rv.status_code, 200)
        self.assertEquals(self.user.api_keys.count(), 1)

