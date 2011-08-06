from django.forms import *
from key.models import *

class ApiKeyForm(ModelForm):
    class Meta:
        model = ApiKey
        
class ApiKeyProfileForm(ModelForm):
    class Meta:
        model = ApiKeyProfile

class ApiKeyAdminForm(ModelForm):
    class Meta:
        model = ApiKey
        readonly_fields = ('key', 'logged_ip')

    def __init__(self, *args, **kwargs):
        super(ApiKeyAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        model = super(ApiKeyAdminForm, self).save(commit=False, *args, **kwargs)
        if not model.key:
            model = generate_unique_key_code(model.profile.user, model)
        if commit:
            model.save()
        return model
