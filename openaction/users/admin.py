from django.contrib import admin
from users.models import *
#from people.models import *

class ProfileAdmin(admin.ModelAdmin):
    pass
#COMMENT LF:    raw_id_fields = ('user', 'person')

admin.site.register(UserProfile, ProfileAdmin)
