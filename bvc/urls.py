from django.conf.urls import url

from . import views

app_name = 'bvc'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^resume-commandes$', views.send_command_summary, name='send_command_summary'),
    url(r'^rappel-mail$', views.subscribe_to_reminder, name='subscribe_to_reminder'),
    url(r'^commande-commission$', views.place_commission_command,
        name='place_commission_command'),
    url(r'^rappel-annulation-commande$', views.contact_unsold_commands,
        name='contact_unsold_commands'),
]
