from django.contrib import admin
from key.models import *
from key.forms import *

class ApiKeyInline(admin.TabularInline):
    model = ApiKey
    extra = 0
    max_num = 0
    fields = ('key', 'logged_ip', 'last_used', 'created')
    readonly_fields = ('key', 'logged_ip')

class ApiKeyAdmin(admin.ModelAdmin):
    form = ApiKeyAdminForm

    def queryset(self, request):
        if request.user.is_superuser:
            return ApiKey.objects.all()
        else:
            p = ApiKeyProfile.objects.get(user=request.user)
            return p.api_keys.all()

class ApiKeyProfileAdmin(admin.ModelAdmin):
    form = ApiKeyProfileAdminForm
    inlines = (ApiKeyInline,)

admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.register(ApiKeyProfile, ApiKeyProfileAdmin)


