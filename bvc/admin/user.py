from django.contrib import admin

from .. import models


admin.site.register(models.user.Member)
admin.site.register(models.user.Commission)
