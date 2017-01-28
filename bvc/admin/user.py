from django.contrib.auth.models import User, Group
from django.contrib import admin

from .site import admin_site
from .. import models


admin_site.register(User)
admin_site.register(Group)
admin_site.register(models.user.Member)
admin_site.register(models.user.Commission)
