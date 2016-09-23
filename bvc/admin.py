from django.contrib import admin

from .models import command

admin.site.register(command.MemberCommand)
admin.site.register(command.CommissionCommand)
