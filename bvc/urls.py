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
]
