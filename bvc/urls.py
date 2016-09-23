from django.conf.urls import url

from . import views

app_name = 'bvc'
urlpatterns = [
    url(r'^$', views.member.home, name='home'),
    url(r'^commander/adherent$', views.member.command_member, name='command_member'),
    url(r'^commander/commission$', views.member.command_commission, name='command_commission'),
]
