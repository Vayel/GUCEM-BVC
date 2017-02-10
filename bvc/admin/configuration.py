from django.contrib import admin

from .site import admin_site
from .. import models


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['id',]

    def has_add_permission(self, request, obj=None):
        return not models.configuration.Configuration.objects.all().count()

    def has_delete_permission(self, request, obj=None):
        return False


admin_site.register(models.configuration.Configuration, ConfigurationAdmin)
