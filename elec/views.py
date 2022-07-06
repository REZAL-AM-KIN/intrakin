from django.shortcuts import render, redirect, HttpResponse
from users.models import Client
from django.db.models import Q, F
from django.core import exceptions
from users.views import index
from elec.forms import itemForm, VirtualitemForm, entree_sortie_matosForm, add_item_to_operationForm
from elec.models import item, place
from elec.models import kind as kind_
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, date

import json

# Create your views here.

def has_group_elec(user):
  h = False
  if user.groups.filter(name='elec').exists():
    h = True
  return h
  
def convertDate2(string):
	L = string.split(" ")
	day = L[0].split("/")
	if len(L) ==2:
		time = L[1].split(":")
	dateTime = day[2]+"-"
	if len(day[1])==1:
		dateTime += "0"
	dateTime += day[1]+"-"
	if len(day[0])==1:
		dateTime += "0"
	dateTime += day[0]
	return(dateTime)  
 
  
@login_required
@user_passes_test(has_group_elec)
def inventaire (request):
	kinds = kind_.objects.filter().values_list('id','name')
	listproduct = item.objects.filter().order_by('associated_kind').values_list('id', 'name', 'brand', 'ref','associated_kind', 'quantity', 'purchase_date', 'state')
	if request.method== 'POST':
		if request.POST.__contains__('edit_product'):
			req_nbr = request.POST.__getitem__('edit_product')
			instance_to_pass = item.objects.filter().order_by('name')[int(req_nbr)]
			return redirect("elec.views.itemedit", id_item = instance_to_pass.pk)
		else :
			messages.error(request, u"Une erreur est survenue")
			return redirect("elec.views.inventaire",{'listproduct' : listproduct})
	return render(request,"elec/inventaire.html", {'listproduct' : listproduct, 'kinds' : kinds})
	

@login_required
@user_passes_test(has_group_elec)
def itemedit(request, id_item):
	locaux = place.objects.filter().values_list('name')
	liste_locaux = []
	for local in locaux :
		liste_locaux.append(str(local[0].encode('utf-8')))
	
	kinds = kind_.objects.filter().values_list('name')
	liste_kinds = []
	for kind in kinds :
		liste_kinds.append(str(kind[0].encode('utf-8')))
	object_to_manage = item.objects.get(pk=id_item)
	if request.method == 'POST':
		form = VirtualitemForm(request.POST, instance = object_to_manage)
		print form
		if form.is_valid():
			form.save()
			messages.success(request, u"Modification reussie !")
			return redirect("elec.views.inventaire")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("elec.views.inventaire")
	else : 
		form = VirtualitemForm(instance = object_to_manage)
	return render(request, "elec/itemedit.html", {'form' : form, 'instance' : object_to_manage.pk, 'liste_locaux' : liste_locaux, 'liste_kinds' : liste_kinds})      

@login_required
@user_passes_test(has_group_elec)
def ajout_matos (request):
	locaux = place.objects.filter().values_list('name')
	liste_locaux = []
	for local in locaux :
		liste_locaux.append(str(local[0].encode('utf-8')))
	
	kinds = kind_.objects.filter().values_list('name')
	liste_kinds = []
	for kind in kinds :
		liste_kinds.append(str(kind[0].encode('utf-8')))
	
	if request.method == 'POST':
		form = itemForm(request.POST)
		if form.is_valid():
			kind_value = form.cleaned_data['kind']
			usual_stockage_value = form.cleaned_data['usual_stockage']
			current_place_value = form.cleaned_data['current_place']
			
			vform = VirtualitemForm()
			vform = vform.save(commit=False)
			vform.name = form.cleaned_data['name']
			vform.brand = form.cleaned_data['brand']
			vform.ref = form.cleaned_data['ref']
			vform.associated_kind = kind_.objects.get(name=kind_value.lower())
			vform.purchase_date = convertDate2(form.cleaned_data['purchase_date'])
			vform.quantity = form.cleaned_data['quantity']
			vform.purchase_value = form.cleaned_data['purchase_value']
			vform.comment = form.cleaned_data['comment']
			vform.state = form.cleaned_data['state']
			vform.usual_stockage = place.objects.get(name=usual_stockage_value.lower())
			vform.current_place = place.objects.get(name=current_place_value.lower())
			vform.save()
			messages.success(request, u"Creation reussie")
			return render(request,"elec/ajout_matos.html", {'liste_locaux' : liste_locaux, 'liste_kinds' : liste_kinds})
		else : 
			messages.error(request, u"Impossible de creer le produit")
			return render(request,"elec/ajout_matos.html", {'liste_locaux' : liste_locaux, 'liste_kinds' : liste_kinds})
	else : 
		form = itemForm()
	return render(request,"elec/ajout_matos.html", {'liste_locaux' : liste_locaux, 'liste_kinds' : liste_kinds})


@login_required
@user_passes_test(has_group_elec)
def entree_sortie_matos(request):

	list_items = item.objects.filter().values_list('id','name','brand','ref').order_by('associated_kind')
	if request.method == 'POST':
		if request.POST.__contains__('quantity') :
			form = add_item_to_operationForm(request.POST)
			print form
			if form.is_valid():
				if form.cleaned_data['quantity'] > item.objects.get(Q(id = form.cleaned_data['quantity'])):
					messages.error(request, u"La quantite demandee est superieure a celle disponible")
					return render(request,"elec/entree_sortie_matos.html",{'list_items' : list_items, 'items_to_manage_display' : items_to_manage_display})
				else :
					try :
						items_to_manage_id=form.items_to_manage_id
						items_to_manage_quantity=form.items_to_manage_quantity
						items_to_manage_id.append(form.cleaned_data['item_id'])
						items_to_manage_quantity.append(form.cleaned_data['quantity'])
					except NameError:
						items_to_manage_id = []
						items_to_manage_quantity = []
						items_to_manage_id.append(form.cleaned_data['item_id'])
						items_to_manage_quantity.append(form.cleaned_data['quantity'])
			else:
				messages.error(request, u"Une erreur s'est produite")
				return render(request,"elec/entree_sortie_matos.html",{'list_items' : list_items})
	else :
		items_to_manage_id = []
		items_to_manage_quantity = []
	if items_to_manage_id != [] :
		items_to_manage_display = (item.objects.filter(id__in = items_to_manage_id).values_list('id', 'name', 'brand', 'ref')).order_by('associated_kind')
	else :
		items_to_manage_display = []
	return render(request,"elec/entree_sortie_matos.html",{'list_items' : list_items, 'items_to_manage_display' : items_to_manage_display, 'items_to_manage_id': items_to_manage_id, 'items_to_manage_quantity' : items_to_manage_quantity})


@login_required
@user_passes_test(has_group_elec)
def about_elec(request):
	return render(request,"elec/about_elec.html")
	