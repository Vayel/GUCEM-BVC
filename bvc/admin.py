from django.contrib import admin

from . import models

class CommandAdmin(admin.ModelAdmin):
    readonly_fields = ['datetime_placed']
    exclude = []

class MemberCommandAdmin(CommandAdmin):
    list_display = ['lastname', 'firstname', 'grouped_command',
                    'datetime_placed', 'state',]
    list_filter = ['state',]

class CommissionCommandAdmin(CommandAdmin):
    list_display = ['commission', 'grouped_command', 'datetime_placed',
                    'state',]
    list_filter = ['commission', 'state',]

class GroupedCommandAdmin(CommandAdmin):
    list_display = ['datetime_placed', 'state', 'state',]
    list_filter = ['state',]

admin.site.register(models.command.MemberCommand, MemberCommandAdmin)
admin.site.register(models.command.CommissionCommand, CommissionCommandAdmin)
admin.site.register(models.command.GroupedCommand, GroupedCommandAdmin)
