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

    def to(self, obj):
        return ', '.join([dest.addr for dest in obj.to.all()])


admin_site.register(models.Email, EmailAdmin)
