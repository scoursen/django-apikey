from django.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from key.models import ApiKey

class KeyForm( ModelForm ):
    class Meta:
        model = ApiKey
        exclude = ( 'user', )
