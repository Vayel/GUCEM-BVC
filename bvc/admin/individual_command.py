from smtplib import SMTPException

from django.contrib import admin, messages
from django.utils.timezone import now

from .site import admin_site
from .. import models


class IndividualCommandAdmin(admin.ModelAdmin):
    actions = ['prepare', 'cancel', 'uncancel', 'warn_about_cancellation',]
    list_filter = ['state',]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def prepare(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.state = models.command.TO_BE_PREPARED_STATE
                cmd.prepare()
            except (ValueError, models.command.InvalidState) as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.ERROR
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    "Une erreur est survenue en envoyant le mail : " + str(e),
                    level=messages.ERROR
                )

    def cancel(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.cancel()
            except models.command.InvalidState as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.ERROR
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    "Une erreur est survenue en envoyant le mail : " + str(e),
                    level=messages.ERROR
                )
    
    def uncancel(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.uncancel()
            except models.command.InvalidState as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.ERROR
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    "Une erreur est survenue en envoyant le mail : " + str(e),
                    level=messages.ERROR
                )
    
    def warn_about_cancellation(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.warn_about_cancellation()
            except models.command.InvalidState as e:
                self.message_user(
                    request,
                    str(e),
                    level=messages.ERROR
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    "Une erreur est survenue en envoyant le mail : " + str(e),
                    level=messages.ERROR
                )
