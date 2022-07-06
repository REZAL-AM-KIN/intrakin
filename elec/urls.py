from django.conf.urls import patterns, include, url
from elec.views import inventaire, ajout_matos, itemedit, about_elec, entree_sortie_matos

urlpatterns = [
	url(r'^inventaire/$', inventaire, name = "inventaire"),
	url(r'^ajout_matos/$', ajout_matos, name = "ajout_matos"),
	url(r'^itemedit/(?P<id_item>\d+)$', itemedit, name="itemedit"),
	url(r'^about_elec/$', about_elec, name = "about_elec"),
	url(r'^entree_sortie_matos/$', entree_sortie_matos, name = "entree_sortie_matos"),
]