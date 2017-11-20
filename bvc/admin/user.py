from django.contrib.auth.models import User, Group
from django.contrib import admin

from .site import admin_site
from .. import models


class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'username']
    search_fields = ('first_name', 'last_name', 'email', 'username')


class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'license', 'club', 'receive_reminder',]
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'user__username')


admin_site.register(User, UserAdmin)
admin_site.register(Group)
admin_site.register(models.Member, MemberAdmin)
admin_site.register(models.Commission)
