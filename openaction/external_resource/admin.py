from django.contrib import admin

from external_resource.models import ExternalResource

class ExternalResourceAdmin(admin.ModelAdmin):

    list_display = ('__unicode__', 'backend_name', 'resource_type', 'first_get_on', 'last_get_on')
    

admin.site.register(ExternalResource, ExternalResourceAdmin)


