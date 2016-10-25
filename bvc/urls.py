from django.conf.urls import url

from . import views

app_name = 'bvc'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^commande_adherent$', views.place_member_command,
        name='place_member_command'),
    url(r'^commande_commission$', views.place_commission_command,
        name='place_commission_command'),
    url(r'^commande_groupee$', views.place_grouped_command,
        name='place_grouped_command'),
]
