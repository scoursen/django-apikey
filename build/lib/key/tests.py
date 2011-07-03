from django.test import TestCase, Client
from django.contrib.auth.models import User
from key.models import ApiKey, ApiKeyProfile, generate_unique_api_key
import hashlib

class ApiKeyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='ApiKeyTest',
                                        email='ApiKeyTest@t.com')
        self.user.save()

    def test_key_generation(self):
        k = generate_unique_api_key(self.user)
        my_kstr = hashlib.md5('%s-%s' % (self.user.email,
                                         k.created)).hexdigest()
        self.assertEquals(my_kstr, k.key)

