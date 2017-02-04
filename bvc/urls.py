from django.conf.urls import url

from . import views

app_name = 'bvc'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^commande-adherent$', views.place_member_command,
        name='place_member_command'),
    url(r'^commande-commission$', views.place_commission_command,
        name='place_commission_command'),
    url(r'^rappel-annulation-commande$', views.contact_unsold_commands,
        name='contact_unsold_commands'),
]
