from django.conf.urls import url

from . import views

app_name = 'bvc'
urlpatterns = [
    url(r'^$', views.member.home, name='home'),
    url(r'^commander/adherent$', views.member.place_member_command,
        name='place_member_command'),
    url(r'^commander/commission$', views.member.place_commission_command,
        name='place_commission_command'),
    url(r'^commander/responsable$', views.manager.place_grouped_command,
        name='place_grouped_command'),
    url(r'^commandes/groupees/lister$', views.manager.list_grouped_commands,
        name='list_grouped_commands'),
    url(r'^commandes/groupees/recevoir/(?P<pk>[0-9]+)$', views.manager.receive_grouped_command,
        name='receive_grouped_command'),
    url(r'^commandes/groupees/preparer/(?P<pk>[0-9]+)$', views.manager.prepare_grouped_command,
        name='prepare_grouped_command'),
]
