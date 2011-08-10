from django.forms import *
import logging
from key.models import *

class ApiKeyProfileAdminForm(ModelForm):
    class Meta:
        model = ApiKeyProfile
        readonly_fields = ('last_access',)

    def clean(self, *args, **kwargs):
        cleaned_data = super(ApiKeyProfileAdminForm, self).clean(*args, **kwargs)
        if self.data.has_key('generate'):
            generate_unique_api_key(self.instance.user)
        return cleaned_data

class ApiKeyAdminForm(ModelForm):
    class Meta:
        model = ApiKey
        readonly_fields = ('key', 'logged_ip')

    def save(self, commit=True, *args, **kwargs):
        model = super(ApiKeyAdminForm, self).save(commit=False, *args, **kwargs)
        if not model.key:
            model = generate_unique_key_code(model.profile.user, model)
        if commit:
            model.save()
        return model
