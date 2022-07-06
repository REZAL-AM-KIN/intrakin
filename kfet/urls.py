from django.conf.urls import patterns, include, url
from kfet.views import getPgs, addtrpg, summarytrpg, cashinputview, getProducts, seuilpg, histopg, bucquageboulc, productcreation, productdisplay, productedit, bucquageboulcgr, remiseNature, reservationCarteMetro, homePians, cvisPians, gestionappros, fournisseurs, uploadfacture, fournisseuredit, approedit, corrStock, entityaccounting

urlpatterns = [
	url(r'^getPgs/$', getPgs, name = "getPgs"),
	url(r'^addtrpg/$', addtrpg, name = "addtrpg"),
	url(r'^summarytrpg/$', summarytrpg, name = "summarytrpg"),
	url(r'^cashinput/$', cashinputview, name = "cashinput"),
	url(r'^remiseNature/$', remiseNature, name = "remiseNature"),
	url(r'^seuilpg/$', seuilpg, name = "seuilpg"),
	url(r'^histopg/$', histopg, name = "histopg"),
	url(r'^getProducts/$', getProducts, name = "getProducts"),
	url(r'^bucquageboulc/$', bucquageboulc, name = "bucquageboulc"),
	url(r'^bucquageboulcgr/$', bucquageboulcgr, name = "bucquageboulcgr"),
	url(r'^productcreation/$', productcreation, name = "productcreation"),
	url(r'^productdisplay/$', productdisplay, name= "productdisplay"),
	url(r'^productedit/(?P<id_product>\d+)$', productedit, name="productedit"),
	url(r'^reservationCarteMetro/$', reservationCarteMetro, name = "reservationCarteMetro"),
	url(r'^gestionappros/$', gestionappros, name = "gestionappros"),
	url(r'^approedit/(?P<id_appro>\d+)$$', approedit, name = "approedit"),
	url(r'^fournisseurs/$', fournisseurs, name = "fournisseurs"),
	url(r'^fournisseuredit/(?P<id_fournisseur>\d+)$$', fournisseuredit, name = "fournisseuredit"),
	url(r'^homePians/$', homePians, name = "homePians"),
	url(r'^cvisPians/$', cvisPians, name = "cvisPians"),
	url(r'^uploadfacture/$', uploadfacture, name = "uploadfacture"),
	url(r'^corrStock/$', corrStock, name = "corrStock"),
	url(r'^entityaccounting/$', entityaccounting, name = "entityaccounting"),
	
]
