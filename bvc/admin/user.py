from django.contrib import admin

from .site import admin_site
from .. import models


admin_site.register(models.user.Member)
admin_site.register(models.user.Commission)
