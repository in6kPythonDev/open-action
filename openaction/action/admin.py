from django.contrib import admin
from action.models import Action#, ActionCategory

class ActionAdmin(admin.ModelAdmin):

    pass

admin.site.register(Action, ActionAdmin)
#admin.site.register(ActionCategory)


