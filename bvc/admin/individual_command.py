from smtplib import SMTPException

from django.contrib import admin, messages
from django.utils.timezone import now
from inline_actions.admin import InlineActionsModelAdminMixin

from .site import admin_site
from .. import models


class IndividualCommandAdmin(InlineActionsModelAdminMixin, admin.ModelAdmin):
    list_filter = ['state',]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_inline_actions(self, request, obj=None):
        actions = super().get_inline_actions(request, obj)
        if obj is None:
            return actions

        if obj.state in (models.command.TO_BE_PREPARED_STATE, models.command.PLACED_STATE):
            actions.append('prepare')
        if obj.state in (models.command.PLACED_STATE, models.command.TO_BE_PREPARED_STATE, models.command.PREPARED_STATE):
            actions.append('cancel')
        if obj.state == models.command.CANCELLED_STATE:
            actions.append('uncancel')

        return actions
    
    def prepare(self, request, cmd, parent_obj=None):
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

    def cancel(self, request, cmd, parent_obj=None):
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
    
    def uncancel(self, request, cmd, parent_obj=None):
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['voucher_stock'] = models.voucher.get_stock()

        return super().changelist_view(request, extra_context=extra_context)
