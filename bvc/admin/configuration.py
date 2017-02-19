from django.contrib import admin

from .site import admin_site
from .. import models


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['id',]

    def get_readonly_fields(self, request, instance=None):
        if instance is None:
            return []

        return [f.name for f in self.model._meta.fields]

    def has_delete_permission(self, request, obj=None):
        return False


admin_site.register(models.configuration.Configuration, ConfigurationAdmin)
