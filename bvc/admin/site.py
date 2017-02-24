from django.contrib.admin import AdminSite
from django.views.decorators.cache import never_cache

from .. import models


class BVCAdminSite(AdminSite):
    site_header = 'Tu faiblis, Dillon !'
    site_title = 'BVC'
    index_title = 'Accueil'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_unsent_mails'] = models.Email.objects.count() > 0
        extra_context['current_grouped_command'] = models.grouped_command.get_current()

        return super().index(request, extra_context)


admin_site = BVCAdminSite(name='bvcadmin')
