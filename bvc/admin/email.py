from django.contrib import admin

from .site import admin_site
from .. import models


class DestAddrInline(admin.StackedInline):
    model = models.email.DestAddr
    verbose_name = 'adresse de destination'
    verbose_name_plural = 'adresses de destination'


class AttachmentInline(admin.StackedInline):
    model = models.email.Attachment
    verbose_name = 'pièce jointe'
    verbose_name_plural = 'pièces jointes'
    extra = 1


class EmailAdmin(admin.ModelAdmin):
    list_display = ['datetime', 'subject', 'to',]
    inlines = [DestAddrInline, AttachmentInline,]
    actions = ['send',]

    def to(self, obj):
        return ', '.join([str(dest) for dest in obj.to.all()])

    def send(self, request, queryset):
        for email in queryset:
            email.to_message().send()
            # If the mail was sent, we do not need it anymore
            # Else, the email backend stored it again, so we remove the duplicate
            email.delete()


admin_site.register(models.Email, EmailAdmin)
