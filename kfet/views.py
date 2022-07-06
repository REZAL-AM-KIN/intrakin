#-*- coding: utf-8 -*-
#SALUT !!!
### POUR LA GESTION DES ACCENTS ###
# chaque fois qu'une fonction 'str' est necessaire il faut que la variable soit encodée en utf8
# il suffit de faire donc : str(variable.encode('utf-8'))
# ainsi tous les caractères spéciaux sont reconnus <3

from operator import itemgetter
from itertools import chain
from django.shortcuts import render, redirect, HttpResponse
from users.models import Client
from kfet.models import transactionboulc, transactionvp, transactionpg, inputmethod, product, entity, cashinput, cartemetro, fournisseur, appros, stockagefacture, category, entity_accounting
from django.db.models import Q, F
from django.core import exceptions
from users.views import index
from kfet.forms import VirtualtransactionpgForm, transactionpgForm, strpgForm, cashinputForm, VirtualcashinputForm, seuilpgForm, histopgForm, VirtualbucquageboulcForm, bucquageboulcForm, productForm, VirtualproductForm, productEditForm, bucquageboulcgrForm, remiseNatureForm, VirtualreservationCarteMetroForm, reservationCarteMetroForm, fournisseurForm, VirtualfournisseurForm, fournisseurEditForm, factureForm, VirtualfactureForm , approsForm, VirtualapprosForm, approEditForm, stockEditForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, date

import json

# Create your views here.

def is_debucquable_check(user):
  c = Client.objects.get(pk = user.pk)
  h = False
  if c.is_debucquable:
    h = True
  return h

def has_group_can_add_money(user):
  h = False
  if user.groups.filter(name='can_add_money').exists():
    h = True
  return h

def has_group_can_create_product(user):
  h = False
  if user.groups.filter(name='can_create_product').exists():
    h = True
  return h

def has_group_can_negats(user):
  h = False
  if user.groups.filter(name='can_negats').exists():
    h = True
  return h

def has_group_can_carte_metro(user):
  h = False
  if user.groups.filter(name='can_carte_metro').exists():
    h = True
  return h

def has_group_gripsserie_cercle(user):
  h = False
  if user.groups.filter(name='gripsserie_cercle').exists():
    h = True
  return h

def has_group_grippserie_boquette(user):
	h = False
	if user.groups.filter(name='gripsserie_boquette').exists():
		h = True
	return h

def list_pg():
	listmatch = Client.objects.order_by('bucque').filter(Q(is_debucquable=1))
	listretour =[]
	for elt in listmatch:
		pg = (elt.nom).encode('utf-8')+" / "+(elt.prenom).encode('utf-8')
		if elt.bucque:
			pg+=(" / "+(elt.bucque).encode('utf-8'))
		if elt.fams:
			pg+=(" / "+(elt.fams).encode('utf-8'))
		listretour.append(pg)
	return(listretour)

def list_product(name_entity):
	listmatch = product.objects.order_by('name').filter(Q(associated_entity__name=name_entity))
	listretour =[]
	for elt in listmatch:
		produit = [elt.pk, (elt.shortcut).encode('utf-8')+" - "+(elt.name).encode('utf-8')+" - "+str(elt.price)+'€']
		listretour.append(produit)
	return(listretour)

def getPgs(request):
  print(Client.objects.filter().values_list('bucque'))
  data = []
  try:
    pg = request.GET.get('pg', '')
    data = Client.objects.filter((Q(bucque__icontains=pg) | Q(nom__icontains=pg) | Q(prenom__icontains=pg) | Q(fams__icontains=pg)) & Q(is_debucquable=1))
  except (KeyError, exceptions.ObjectDoesNotExist, ValueError):
    pass
  tmp = {}
  tmp["results"] = []
  for i in data:
    if i.bucque:
      tmp["results"].append({"title": str((i.nom).encode('utf-8') + ' / ' + (i.prenom).encode('utf-8') + ' / ' + (i.bucque).encode('utf-8') + ' / ' + (i.fams).encode('utf-8'))})
    else:
      tmp["results"].append({"title": (i.nom).encode('utf-8') + ' / ' + (i.prenom).encode('utf-8')})
  return HttpResponse(json.dumps(tmp), content_type = "text/javascript")

def convertDate(string):
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
	dateTime += day[0]+" "
	if len(L) ==2:
		if len(time[0])==1:
			dateTime += "0"
		dateTime += time[0]+":"
		dateTime += time[1]+":00"
	return(dateTime)

def convertDate1(string):
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

def getProducts(request):
  data = []
  grp = request.user.groups.all().values_list('name')
  ent = entity.objects.filter(Q(name__in=grp))
  try:
    field = request.GET.get('prod', '')
    data = product.objects.filter(((Q(name__icontains=field) & Q(associated_entity__in=ent)) | (Q(associated_entity__in=ent) & Q(shortcut__icontains=field))))
  except (KeyError, exceptions.ObjectDoesNotExist, ValueError):
    pass
  tmp = {}
  tmp["results"] = []
  for i in data:
    tmp["results"].append({"title": str((i.name).encode('utf-8') + '  / (' + (i.shortcut).encode('utf-8') + ')')})
  return HttpResponse(json.dumps(tmp), content_type = "text/javascript")

def getHisto(pkpg):
  tpg_list=transactionpg.objects.filter((Q(target = pkpg) | Q(source = pkpg)) & Q(accepted = True))
  tbc_list=transactionboulc.objects.filter(Q(target = pkpg))
  tvp_list=transactionvp.objects.filter(Q(target = pkpg))
  tci_list=cashinput.objects.filter(Q(target = pkpg))

  query_result = sorted(chain(tpg_list, tbc_list, tvp_list, tci_list), key=lambda instance: instance.date, reverse=True)
  listmatch = []
  for result in query_result:
    inter_listmatch=[]
    if result.__class__.__name__ == "transactionpg":
      current_result = result
      bucque_field = getattr(getattr(current_result, 'source'),'bucque')
      target_bucque_field = getattr(getattr(current_result, 'target'),'bucque')
      inter_listmatch.extend([bucque_field, getattr(current_result,'amount'),getattr(current_result, 'description'),getattr(current_result, 'date'),target_bucque_field, "trpg"])
    elif result.__class__.__name__ == "transactionboulc":
      current_result = result
      bucque_field = getattr(current_result, 'entite')
      authortb_field = getattr(getattr(current_result, 'authortb'),'bucque')
      inter_listmatch.extend([bucque_field, getattr(current_result, 'product_price'), getattr(current_result, 'product_name'), getattr(current_result, 'date'), authortb_field, "trb"])
    elif result.__class__.__name__ == "transactionvp":
      current_result = result
      bucque_field = getattr(current_result, 'entite')
      inter_listmatch.extend([bucque_field, getattr(current_result, 'product_price'), getattr(current_result, 'product_name'), getattr(current_result, 'date'), getattr(current_result, 'authortvp'), "trvp"])
    elif result.__class__.__name__ == "cashinput":
      current_result = result
      bucque_field = getattr(getattr(current_result, 'target'), 'bucque')
      authorci_field = getattr(getattr(current_result, 'authorci'),'bucque')
      inter_listmatch.extend([bucque_field, getattr(current_result, 'amount'), getattr(current_result, 'method'), getattr(current_result, 'date'), authorci_field, "ci"])
    listmatch.append(inter_listmatch)
  return(listmatch)


def var_stock(produit, quantity, add):					# Permet de changer le stock d'un produit / add=True pour un ajout, add=False pour un retrait
  	prd=produit.pk
  	quantite = product.objects.filter(id=prd)
  	if add:
  		if (quantite.values_list("stock"))[0][0] == None:
  			quantite.update(stock=0)
  			messages.info(u"Ce produit ne disposait pas de stock initial, si vous voulez en ajouter un, allez dans l'onglet de correction de stock")
  		quantite.update(stock=F('stock')+quantity)
  	else:
  		if (quantite.values_list("stock"))[0][0]:
  			if int((quantite.values_list("stock"))[0][0]) <= 0:
  				messages.info(u"Contrôlez votre stock de produit !")
  			else:
  				quantite.update(stock=F('stock')-quantity)
  		else:
  			return


@login_required
@user_passes_test(is_debucquable_check)
def addtrpg(request):
  if request.method == 'POST':
    form = transactionpgForm(request.POST)
    if form.is_valid():
      trgt = Client.objects.get(pk = request.user.pk)
      fcd=str((form.cleaned_data['pg']).encode('utf-8')).lower().split(" / ")
      src = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
      amnt = form.cleaned_data['amount']
      descrip = form.cleaned_data['description']
      vform = VirtualtransactionpgForm()
      vform = vform.save(commit=False)
      vform.target=src
      vform.source=trgt
      vform.amount=amnt
      vform.description=descrip
      if src != trgt and amnt > 0:
        vform.save()
        messages.success(request, u"Demande effectuée")
        return redirect("kfet.views.summarytrpg")
      else:
        messages.error(request, u"Une erreur est survenue")
        return redirect("kfet.views.addtrpg")
    else:
      messages.error(request, u"Une erreur est survenue")
      return redirect("kfet.views.addtrpg")
  else:
    form=transactionpgForm()
  return render(request, "kfet/addtrpg.html")

@login_required
@user_passes_test(is_debucquable_check)
def summarytrpg(request):
  b = Client.objects.get(pk = request.user.pk)
  listtrpgdone = transactionpg.objects.filter(Q(source = b) & Q(accepted = 0)).values_list('target__nom','amount','description','date')
  listtrpgtodo = transactionpg.objects.filter(Q(target = b) & Q(accepted = 0)).values_list('source__nom', 'amount', 'description')
  if request.method == 'POST':
    req = request.POST.__getitem__('idnbr')
    trpgtodo = transactionpg.objects.filter(Q(target = b) & Q(accepted = 0))
    formfilling = trpgtodo[int(req)]
    form = strpgForm(instance=formfilling)
    form = form.save(commit = False)
    if b.credit >= form.amount:
      form.accepted = 1
      form.save()
      Client.debitpg(b, form.amount)
      Client.creditpg(form.source, form.amount)
      messages.success(request, u"Transaction effectuée")
      return redirect("kfet.views.summarytrpg")
    else:
      messages.warning(request, u"Tu n'as pas assez d'argent !")
      return redirect("kfet.views.summarytrpg")
  return render(request, "kfet/strpg.html", {'donelist' : listtrpgdone, 'todolist' : listtrpgtodo})

@login_required
@user_passes_test(has_group_can_add_money)
def cashinputview(request):
  if request.method == 'POST':
    form = cashinputForm(request.POST)
    print form
    if form.is_valid():
      authorci=Client.objects.get(pk = request.user.pk)
      fcd=str((form.cleaned_data['pg']).encode('utf-8')).lower().split(" / ")
      trgt = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
      amnt = form.cleaned_data['amount']
      im=inputmethod.objects.get(name = form.cleaned_data['method'])
      print im
      vform = VirtualcashinputForm()
      vform = vform.save(commit=False)
      vform.authorci=authorci
      vform.target=trgt
      vform.amount=amnt
      vform.method=im
      if amnt > 0:
        vform.save()
        Client.creditpg(trgt,amnt)
        messages.success(request, u"Ajout effectué !")
        return redirect("kfet.views.cashinputview")
      else:
        messages.warning(request, u"Le montant doit etre positif !")
        return redirect("kfet.views.cashinputview")
    else:
      messages.error(request, u"Une erreur est survenue")
      return redirect("kfet.views.cashinputview")
  else:
    form = cashinputForm()
  return render(request, "kfet/cashinput.html", {'form' : form})

@login_required
@user_passes_test(has_group_can_negats)
def seuilpg(request):
  if request.method == 'POST':
    form = seuilpgForm(request.POST)
    if form.is_valid():
      montant = form.cleaned_data['seuil']
      if str(form.cleaned_data['proms']) != "...":
        promos = str(form.cleaned_data['proms']).lower().split(";")
        for elt in promos:
          if not elt.isdigit():
            messages.error(request, u"Mauvaise saisie des prom's")
            return render(request, "kfet/seuilpg.html")
        listmatch = []
        for i in range(len(promos)):
          listmatch += Client.objects.filter(Q(credit__lt=montant) & Q(proms = promos[i])).values_list('nom','prenom','proms','credit')
      else:
        listmatch = Client.objects.filter(Q(credit__lt=montant)).values_list('nom','prenom','proms','credit')
      if len(listmatch) == 0:
        messages.error(request, u"Aucun PG ne correspond")
        return render(request, "kfet/seuilpg.html")
      else:
        print(listmatch)
        return render(request, "kfet/seuilpg.html", {'listmatch' : listmatch})
    else:
      messages.error(request, u"Une erreur est survenue")
      return render(request, "kfet/seuilpg.html")
  else:
    form = seuilpgForm()
  return render(request, "kfet/seuilpg.html")

@login_required
def histopg(request):
  if request.method == 'POST':
    form = histopgForm(request.POST)
    if form.is_valid():
      fcd=str((form.cleaned_data['pg']).encode('utf-8')).lower().split(" / ")
      pkpg = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd)).pk
      bucquepg = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd)).bucque
      if len(fcd) == 0:
        messages.error(request, u"Aucun PG ne correspond")
        return render(request, "kfet/histopg.html")
    else:
      messages.error(request, u"Une erreur est survenue")
      return render(request, "kfet/histopg.html")
  else:
    form = histopgForm()
    pkpg = Client.objects.filter(Q(pk = request.user.pk)).values_list('pk')
    bucquepg = Client.objects.get(Q(pk = request.user.pk)).bucque

  listmatch=getHisto(pkpg)

  return render(request, "kfet/histopg.html", {'listmatch' : listmatch, 'bucquepg' : bucquepg})

@login_required
@user_passes_test(has_group_can_create_product)
def bucquageboulc(request):
  if request.method== 'POST':
    form  = bucquageboulcForm(request.POST)
    if form.is_valid():
      authortb=Client.objects.get(pk = request.user.pk)
      fcd=str((form.cleaned_data['pg']).encode('utf-8')).lower().split(" / ")
      try:
        target = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
        product_to_search=str((form.cleaned_data['prod']).encode('utf-8')).lower().split(" / ")
        product_to_apply=product.objects.get(Q(name__in=product_to_search))
        product_price=product_to_apply.price
        product_name=product_to_apply.name
        entite=product_to_apply.associated_entity
        target_credit = target.credit
        if request.user.groups.filter(name='can_negats').exists() or target_credit >= product_price:
          vform = VirtualbucquageboulcForm()
          vform = vform.save(commit=False)
          vform.authortb=authortb
          vform.target=target
          vform.product_price=product_price
          vform.product_name=product_name
          vform.entite=entite
          vform.save()
          Client.debitpg(target,product_price)
          var_stock(product_to_apply, "1", False)
          messages.success(request, u"Bucquage effectué")
          return render(request, "kfet/bucquageboulc.html")
        else:
          messages.error(request, u"Pas assez d'argent sur le compte cible")
          return render(request, "kfet/bucquageboulc.html")
      except Client.DoesNotExist :
          messages.error(request, "Ce PG n'existe pas...")
    else:
      messages.error(request, u"Une erreur est survenue")
      return render(request, "kfet/bucquageboulc.html")
    return render(request, "kfet/bucquageboulc.html")

  else:
    form=bucquageboulcForm()
  return render(request, "kfet/bucquageboulc.html")

@login_required
@user_passes_test(has_group_can_create_product)
def productcreation(request):

  entites = entity.objects.filter().values_list('name')
  liste_entites = []
  for entite in entites:
    liste_entites.append(str(entite[0].encode('utf-8')))
  categories = category.objects.filter().values_list('name')
  liste_categories = []
  for categorie in categories:
    liste_categories.append(str(categorie[0].encode('utf-8')))

  if request.method == 'POST':
    form = productForm(request.POST)
    print form
    if form.is_valid():
      name = form.cleaned_data['name']
      price = form.cleaned_data['price']
      categoryvalue = form.cleaned_data['category']
      entityvalue = form.cleaned_data['entity']
      shortcut = form.cleaned_data['shortcut']
      stock = form.cleaned_data['stock']
      if price < 0:
      	messages.error(request, u"Impossible de créer un produit à prix négatif")
        return render(request, "kfet/productcreation.html")
      else:
	      if request.user.groups.filter(name=entityvalue.lower()).exists():
	        vform = VirtualproductForm()
	        vform = vform.save(commit=False)
	        vform.name = name
	        vform.price = price
	        vform.associated_category=category.objects.get(name = categoryvalue.lower())
	        vform.shortcut = shortcut
	        vform.stock = stock
	        vform.associated_entity=entity.objects.get(name = entityvalue.lower())
	        vform.favorite = 0
	        vform.enable = 1
	        vform.save()
	        messages.success(request, u"Création réussie")
	        return render(request, "kfet/productcreation.html",{'liste_entites' : liste_entites, 'liste_categories' : liste_categories})
	      else:
	        form = productForm()
	        messages.error(request, u"Impossible de créer le produit pour l'entité sélectionnée")
	        return render(request, "kfet/productcreation.html",{'liste_entites' : liste_entites, 'liste_categories' : liste_categories})
    else:
      messages.error(request, u"Une erreur est survenue")
      return render(request, "kfet/productcreation.html",{'liste_entites' : liste_entites, 'liste_categories' : liste_categories})
  else:
    form = productForm()
  return render(request, "kfet/productcreation.html",{'liste_entites' : liste_entites, 'liste_categories' : liste_categories})

@login_required
@user_passes_test(has_group_can_create_product)
def productdisplay(request):
  current_user_group = request.user.groups.all().values_list('name')
  user_entity = entity.objects.filter(Q(name__in=current_user_group))
  list_existing_product = (product.objects.filter(Q(associated_entity__in=user_entity)).values_list('id', 'name', 'price', 'shortcut','associated_category__name', 'stock', 'enable', 'favorite')).order_by('name')

  #list_existing_product = product.objects.filter(Q(associated_entity__in=user_entity)).values_list('id','name','price','shortcut', 'associated_category', 'stock','enable','favorite').order_by('name')
  #products = product.objects.filter(Q(associated_entity__in=user_entity)).values_list('id','name','price','shortcut', 'associated_category', 'stock','enable','favorite').order_by('name')
  #print(products)
  #products.query.join((None, 'product', None, None))
  #connection = ('product', 'product_associated_category', 'id', 'product_id')
  #products.query.join(connection, promote=True)
  #connection = ('product_associated_category', 'associated_category', 'associated_category_id', 'id')
  #products.query.join(connection, promote=True)
  #print(products)
  if request.method == 'POST':
    if request.POST.__contains__('edit_product'):
      req_nbr = request.POST.__getitem__('edit_product')
      instance_to_pass = product.objects.filter(Q(associated_entity__in=user_entity)).order_by('name')[int(req_nbr)]
      return redirect("kfet.views.productedit", id_product = instance_to_pass.pk)
    elif request.POST.__contains__('remove_favorite'):
      id_product_to_manage = request.POST.__getitem__('remove_favorite')
      product_to_edit = product.objects.get(Q(associated_entity__in=user_entity) & Q(id = id_product_to_manage))
      product_to_edit.favorite = 0
      product_to_edit.save()
      messages.success(request, u"Modification réussie")
    elif request.POST.__contains__('make_favorite'):
      id_product_to_manage = request.POST.__getitem__('make_favorite')
      product_to_edit = product.objects.get(Q(associated_entity__in=user_entity) & Q(id = id_product_to_manage))
      product_to_edit.favorite = 1
      product_to_edit.save()
      messages.success(request, u"Modification réussie")
    elif request.POST.__contains__('enable'):
      id_product_to_manage = request.POST.__getitem__('enable')
      product_to_edit = product.objects.get(Q(associated_entity__in=user_entity) & Q(id = id_product_to_manage))
      product_to_edit.enable = 1
      product_to_edit.save()
      messages.success(request, u"Activation réussie")
    elif request.POST.__contains__('disable'):
      id_product_to_manage = request.POST.__getitem__('disable')
      product_to_edit = product.objects.get(Q(associated_entity__in=user_entity) & Q(id = id_product_to_manage))
      product_to_edit.enable = 0
      product_to_edit.save()
      messages.success(request, u"Désactivation réussie")
#      print id_product_to_manage, type(id_product_to_manage), product_to_edit
#    elif request.POST.__contains__('delete_product'):
#      req_nbr = request.POST.__getitem__('delete_product')
#      instance_to_pass = product.objects.filter(Q(associated_entity__in=user_entity))[int(req_nbr)]
#      if getattr(instance_to_pass, 'name') == list_existing_product[int(req_nbr)][0]:
#        instance_to_pass.delete()
#        messages.success(request, u"Suppression réussie !")
#        return redirect("kfet.views.productdisplay")
    else:
    	messages.error(request, u"Une erreur est survenue")
    	return redirect("kfet.views.productdisplay")
  return render(request, "kfet/productdisplay.html", {'listproduct' : list_existing_product})

@login_required
@user_passes_test(has_group_can_create_product)
def productedit(request, id_product):
	object_to_manage = product.objects.get(pk=id_product)
	current_user_group = request.user.groups.all().values_list('name')
	user_entity = entity.objects.filter(Q(name__in=current_user_group))
	auth = False
	for i in user_entity:
		auth=bool(str(i) == "cvis")
	if request.method == 'POST':
		form = productEditForm(request.POST, instance = object_to_manage)
		print form
		if form.is_valid():
			form.save()
			messages.success(request, u"Modification réussie !")
			return redirect("kfet.views.productdisplay")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("kfet.views.productdisplay")
	else:
		form = productEditForm(instance = object_to_manage)
#	print info_enable, info_favorite
	return render(request, "kfet/productedit.html", {'form' : form, 'instance' : object_to_manage.pk})


@login_required
@user_passes_test(has_group_can_create_product)
def bucquageboulcgr(request):
  if request.method== 'POST':
    form  = bucquageboulcgrForm(request.POST)
    if form.is_valid():
      authortb=Client.objects.get(pk = request.user.pk)
      pgs=str((form.cleaned_data['pgs']).encode('utf-8'))
      pgs=pgs.split("|$|")
      pg_riche = "Bucquage effectué pour les PGs suivants : "
      pg_pauvre = "Pas assez d'argent sur les comptes suivants : "
      for pg in pgs[:-1]:
        fcd=str(pg).lower().split(" / ")
        try:
          target = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
          product_to_search=str((form.cleaned_data['prod']).encode('utf-8')).lower().split(" / ")
          product_to_apply=product.objects.get(Q(name__in=product_to_search))
          product_price=product_to_apply.price
          product_name=product_to_apply.name
          entite=product_to_apply.associated_entity
          target_credit = target.credit
          if request.user.groups.filter(name='can_negats').exists() or target_credit >= product_price:
            vform = VirtualbucquageboulcForm()
            vform = vform.save(commit=False)
            vform.authortb=authortb
            vform.target=target
            vform.product_price=product_price
            vform.product_name=product_name
            vform.entite=entite
            vform.save()
            var_stock(product_to_apply, "1", False)
            Client.debitpg(target,product_price)
            pg_riche += (str(target.prenom) +" "+ str(target.nom) +" -- ")
          else:
            pg_pauvre += (str(target.prenom) +" "+ str(target.nom) +" -- ")
        except Client.DoesNotExist :
          messages.error(request, ("Le PG ' "+pg+" ' n'existe pas..."))
      if pg_pauvre == "Pas assez d'argent sur les comptes suivants : ":
        pg_riche = "Bucquage effectué pour tous les PG selectionnés (sauf PG inexistants)"
        messages.success(request, pg_riche)
      elif pg_riche == "Bucquage effectué pour les PG suivants : ":
        pg_pauvre == "Pas assez d'argent sur les comptes des PG selectionnés"
        messages.error(request, pg_pauvre)
      else:
        messages.error(request, pg_pauvre)
        messages.success(request, pg_riche)
      return render(request, "kfet/bucquageboulcgr.html")
    else:
      messages.error(request, u"Une erreur est survenue :")
      return render(request, "kfet/bucquageboulcgr.html")
    return render(request, "kfet/bucquageboulcgr.html")

  else:
    form=bucquageboulcgrForm()
  return render(request, "kfet/bucquageboulcgr.html")

@login_required
@user_passes_test(has_group_can_add_money)
def remiseNature(request):
	if request.method == 'POST':
		form = remiseNatureForm(request.POST)
		if form.is_valid():
			authorrn=Client.objects.get(pk = request.user.pk)
			fcd=str((form.cleaned_data['pg']).encode('utf-8')).lower().split(" / ")
			amnt = form.cleaned_data['amount']
			try:
				target = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
				target_credit = target.credit
				im=inputmethod.objects.get(name = 'Remise Nature')

				if request.user.groups.filter(name='can_negats').exists() or target_credit >= amnt:
					vform = VirtualcashinputForm()
					vform = vform.save(commit=False)
					vform.authorci=authorrn
					vform.target=target
					vform.amount=amnt
					print(type(amnt))
					vform.method=im
					if amnt > 0 :
						vform.save()
						Client.debitpg(target,amnt)
						messages.success(request, u"Remise Nature effectuée")
						return redirect("kfet.views.remiseNature")
					else :
						messages.warning(request, u"Le montant doit être positif")
						return redirect("kfet.views.remiseNature")
				else:
					messages.error(request, u"Une erreur est survenue")
					return redirect("kfet.views.remiseNature")
			except Client.DoesNotExist :
				messages.error(request, u"Une erreur est survenue")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("kfet.views.remiseNature")
	else:
		form=remiseNatureForm()
	return render(request, "kfet/remiseNature.html",{'form' : form})

@login_required #accessible aux personnes authentifiées
@user_passes_test(has_group_can_carte_metro) #possède le groupe "can_carte_metro"
def reservationCarteMetro(request): #definition de la page
	entites = entity.objects.filter().values_list('name')  #on récupère les entités rattachées à l'utilisateur
	liste_entites = [] #on en crée une liste pour récupérer que le nom et les mettre en forme
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST': #condition vérifiée quand l'utilisateur soumet un formulaire
		form = reservationCarteMetroForm(request.POST) #on défini le formulaire à utiliser pour recueillir les données
		print(form)
		if request.POST.__contains__('desired_date') : #commme on a plusieurs formulaires, on regarde ce que contient celui qui a été soumis
			if form.is_valid(): #on vérifie que les données entrées sont valides par rapport aux conditions définies dans kfet/forms.py pour reservationCarteMetroForm
				publisher = Client.objects.get(pk = request.user.pk) #on récupère l'id de l'utilisateur qui a soumis le formulaire
				desired_date = convertDate(form.cleaned_data['desired_date']) #on converti la date dans le bon format pour la BDD le .cleaned_data permet de récuperer des donnees saines
				associated_entity = form.cleaned_data['associated_entity'] #les données du formulaire sont transférées du HTML au python sous le type d'un dictionnaire, pour récupérer la donnée désirée ça marche comme une liste mais avec le nom de l'élément et non son numéro d'index
				description = form.cleaned_data['description']
				if request.user.groups.filter(name=associated_entity.lower()).exists(): #on vérifie que l'entité existe (en cas de modification du HTML de la page dans le naviigateur..)
					vform=VirtualreservationCarteMetroForm() #on défini notre vform qui va faire l'interface entre le python et la BDD
					vform=vform.save(commit=False) #à faire (lié à la ligne précédente)
					vform.publisher=publisher #on reprend les données de notre form pour les mettre dans le vform
					vform.associated_entity=entity.objects.get(name = associated_entity.lower()) #on veut stocker l'id de l'entite dans la BDD et non pas son nom. Le entity.objects.get(name = associated_entity.lower()) correspond à une requete SQL : SELECT (élément défini dans le return du model dans models.py) FROM entity WHERE name = associated_entity.lower()
					vform.desired_date=desired_date
					vform.description=description
					vform.save() #equivalent au conn.commit en Flask
					messages.success(request, u"Demande envoyée, en attente d'approbation")
				else:
					messages.error(request, u"Impossible de créer la demande pour la boquette sélectionnée") #l'utilisateur aurait truandé le HTML pour s'octroyer des droits qu'il n'a pas, donc on le valide !!
			else:
				messages.error(request, u"Formulaire invalide")


		elif request.POST.__contains__('accept_resa'): #l'utilisateur a cliquer sur un des boutons Valider
			id_resa_to_manage = request.POST.__getitem__('accept_resa') #la variable renvoyer par le HTML est accept_resa et a pour valeur l'id de la réservation en question
			resa_to_manage = cartemetro.objects.get(Q(id = id_resa_to_manage)) #on récupère toutes les infos de la réservation concernée /!\ le GET s'utilise quand on n'a qu'une seule ligne à récupérer
			resa_to_manage.accepted = 'validated' #équivalent de INSERT INTO, on peut directement modifier les données de la réservation
			resa_to_manage.decision_date = datetime.now()
#			print request.user.pk
			resa_to_manage.decision_by = Client.objects.get(pk = request.user.pk) #on ne stocke que l'id de l'utilisateur
			resa_to_manage.save() #applique les modifications à la ligne concernée
			messages.success(request, u"Réservation validée")

		elif request.POST.__contains__('refuse_resa'):
			id_resa_to_manage = request.POST.__getitem__('refuse_resa')
			resa_to_manage = cartemetro.objects.get(Q(id = id_resa_to_manage))
			resa_to_manage.accepted = 'cancelled'
			resa_to_manage.decision_date = datetime.now()
			resa_to_manage.decision_by = Client.objects.get(pk = request.user.pk)
			resa_to_manage.save()
			messages.success(request, u"Annulation prise en compte")
		else :
			messages.error(request, u"Un problème est survenu")

	#on va devoir générer la liste contenant les lignes des réservation à afficher dans le tableau
	listeresacartemetro=[]
	query_result = cartemetro.objects.filter(desired_date__gte = datetime.now()).order_by('desired_date') #permet de sélectionner uniquement les demandes qui concernent des dates à venir et de récupérer les lignes concernées
	for result in query_result : #on parcours les réservations concernées
		resa=[]
		current_result = result
		resa_id=getattr(current_result, 'id') #on en extrait les éléments souhaités dans l'ordre que l'on souhaite pour faciliter le travail en HTML
		resa_desired_date=getattr(current_result,'desired_date')
		resa_publisher=getattr(current_result,'publisher')
		resa_entity=getattr(current_result,'associated_entity')
		resa_description=getattr(current_result, 'description')
		resa_status = getattr(current_result, 'accepted')
		resa_decision_by = getattr(current_result, 'decision_by')
		resa.extend([resa_id,resa_desired_date,resa_publisher,resa_entity,resa_description,resa_status,resa_decision_by]) #on crée 1 LISTE PAR RESA
		listeresacartemetro.append(resa) #que l'on vient ajouter à une liste de résaS
	return render(request, "kfet/reservationcartemetro.html",{'liste_entites' : liste_entites, 'listeresacartemetro' : listeresacartemetro}) #on indique ici quel template (HTML)  utiliser ainsi que les variables que l'on souhaite transmettre du python vers le HTML (le nom entre '' est celui du HTML)


@login_required
@user_passes_test(has_group_can_create_product)
def gestionappros(request):
	current_user_group = request.user.groups.all().values_list('name')
	user_entity = entity.objects.filter(Q(name__in=current_user_group))
	list_existing_appro = appros.objects.filter(Q(entity__in=user_entity)).values_list('num_facture', 'date','product__name','product_price', 'quantity', 'enable').order_by('-date')
	entites = entity.objects.filter().values_list('name')
	liste_entites = []
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST':
		if request.POST.__contains__('entity'):
			form = approsForm(request.POST)
			print form
			if form.is_valid():
				num_facture = form.cleaned_data['num_facture']
				entityvalue = form.cleaned_data['entity']
				date = convertDate1(form.cleaned_data['date'])
				product_price = form.cleaned_data['product_price']
				quantity = form.cleaned_data['quantity']
  				if product_price < 0 or quantity < 0 :
  					messages.error(request, u"Vérifiez vos données (prix ou stock négatifs)")
  					return render(request, "kfet/gestionappros.html")
  				else:
  					product_to_search=str((form.cleaned_data['product']).encode('utf-8')).lower().split(" / ")
  					product_to_apply=product.objects.get(Q(name__in=product_to_search))
  					if request.user.groups.filter(name=entityvalue.lower()).exists():
  						vform = VirtualapprosForm()
  						vform = vform.save(commit=False)
  						vform.num_facture = num_facture
  						vform.entity = entity.objects.get(name = entityvalue.lower())
  						vform.date = date
  						vform.product_price = product_price
  						vform.product = product_to_apply
  						vform.quantity = quantity
  						vform.save()
  						var_stock(product_to_apply, quantity, True) # True pour des appros, False pour un débucquage
  						messages.success(request, u"Ajout réussi")
  						return render(request, "kfet/gestionappros.html",{'liste_entites' : liste_entites, 'listappro' : list_existing_appro})
  					else:
  						form = approsForm()
  						messages.error(request, u"Impossible d'ajouter l'appro pour l'entité sélectionnée")
  						return render(request, "kfet/gestionappros.html",{'liste_entites' : liste_entites, 'listappro' : list_existing_appro})
  			else:
  				messages.error(request, u"Une erreur est survenue")
  				return render(request, "kfet/gestionappros.html",{'liste_entites' : liste_entites, 'listappro' : list_existing_appro})
		elif request.POST.__contains__('edit_appro'):
			req_nbr = request.POST.__getitem__('edit_appro')
			instance_to_pass = appros.objects.filter(Q(entity__in=user_entity)).order_by('-date')[int(req_nbr)]
			return redirect("kfet.views.approedit", id_appro = instance_to_pass.pk)
		elif request.POST.__contains__('enable'):
			req_nbr = request.POST.__getitem__('enable')
			appro_to_manage = appros.objects.filter(Q(entity__in=user_entity)).order_by('-date')[int(req_nbr)]
			id_appro_to_manage=appro_to_manage.pk
			print(appro_to_manage.pk)
			appro_to_edit = appros.objects.get(Q(entity__in=user_entity) & Q(id = id_appro_to_manage))
			appro_to_edit.enable = 1
			appro_to_edit.save()
			messages.success(request, u"Activation réussie")
		elif request.POST.__contains__('disable'):
			id_appro_to_manage = request.POST.__getitem__('disable')
			appro_to_edit = appros.objects.get(Q(entity__in=user_entity) & Q(id = id_appro_to_manage))
			appro_to_edit.enable = 0
			appro_to_edit.save()
			messages.success(request, u"Désactivation réussie")
		else:
  			form = productForm()
  			return render(request, "kfet/gestionappros.html",{'liste_entites' : liste_entites, 'listappro' : list_existing_appro})
  	return render(request, "kfet/gestionappros.html",{'liste_entites' : liste_entites, 'listappro' : list_existing_appro})

@login_required
@user_passes_test(has_group_can_create_product)
def approedit(request, id_appro):
	object_to_manage = appros.objects.get(pk=id_appro)
	if request.method == 'POST':
		form = approEditForm(request.POST, instance = object_to_manage)
		print form
		if form.is_valid():
			form.save()
			messages.success(request, u"Modification réussie !")
			return redirect("kfet.views.gestionappros")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("kfet.views.gestionappros")
	else:
		form = approEditForm(instance = object_to_manage)
	return render(request, "kfet/approedit.html", {'form' : form, 'instance' : object_to_manage.pk})


@login_required
@user_passes_test(has_group_can_create_product)
def fournisseurs(request):
	current_user_group = request.user.groups.all().values_list('name')
	user_entity = entity.objects.filter(Q(name__in=current_user_group))
	list_existing_fournisseur = fournisseur.objects.filter(Q(associated_entity__in=user_entity)).values_list('name','tel','adress','mail','remark').order_by('name')
	entites = entity.objects.filter().values_list('name')
	liste_entites = []
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST':
		if request.POST.__contains__('edit_fournisseur'):
			req_nbr = request.POST.__getitem__('edit_fournisseur')
			instance_to_pass = fournisseur.objects.filter(Q(associated_entity__in=user_entity)).order_by('name')[int(req_nbr)]
			return redirect("kfet.views.fournisseuredit", id_fournisseur = instance_to_pass.pk)
		elif request.POST.__contains__('delete_fournisseur'):
			req_nbr = request.POST.__getitem__('delete_fournisseur')
			instance_to_pass = fournisseur.objects.filter(Q(associated_entity__in=user_entity))[int(req_nbr)]
			if getattr(instance_to_pass, 'name') == list_existing_fournisseur[int(req_nbr)][0]:
				instance_to_pass.delete()
				messages.success(request, u"Suppression réussie !")
				return redirect("kfet.views.fournisseurs")
			else:
				messages.error(request, u"Une erreur est survenue")
				return redirect("kfet.views.fournisseurs")
		elif request.POST.__contains__('entity'):
			form = fournisseurForm(request.POST)
			print form
			if form.is_valid():
				entityvalue = form.cleaned_data['entity']
				if request.user.groups.filter(name=entityvalue.lower()).exists():
					vform = VirtualfournisseurForm()
					vform = vform.save(commit=False)
					vform.name = form.cleaned_data['name']
					vform.tel = form.cleaned_data['tel']
					vform.adress = form.cleaned_data['adress']
					vform.mail = form.cleaned_data['mail']
					vform.remark = form.cleaned_data['remark']
					entityvalue = form.cleaned_data['entity']
					vform.entity = entity.objects.get(name = entityvalue.lower())
					vform.save()
					messages.success(request, u"Ajout réussi")
					return render(request, "kfet/fournisseurs.html",{'liste_entites' : liste_entites, 'listfournisseur' : list_existing_fournisseur})
				else:
					form = approsForm()
  					messages.error(request, u"Impossible d'ajouter le fournisseur à l'entité sélectionnée")
  					return render(request, "kfet/fournisseurs.html",{'liste_entites' : liste_entites, 'listfournisseur' : list_existing_fournisseur})
			else:
				messages.error(request, u"Une erreur est survenue")
  				return render(request, "kfet/fournisseurs.html",{'liste_entites' : liste_entites, 'listfournisseur' : list_existing_fournisseur})
  		else:
  			form = productForm()
  			return render(request, "kfet/fournisseurs.html",{'liste_entites' : liste_entites, 'listfournisseur' : list_existing_fournisseur})
	return render(request, "kfet/fournisseurs.html", {'liste_entites' : liste_entites, 'listfournisseur' : list_existing_fournisseur})



@login_required
@user_passes_test(has_group_can_create_product)
def fournisseuredit(request, id_fournisseur):
	object_to_manage = fournisseur.objects.get(pk=id_fournisseur)
	if request.method == 'POST':
		form = fournisseurEditForm(request.POST, instance = object_to_manage)
		print form
		if form.is_valid():
			form.save()
			messages.success(request, u"Modification réussie !")
			return redirect("kfet.views.fournisseurs")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("kfet.views.fournisseurs")
	else:
		form = fournisseurEditForm(instance = object_to_manage)
	return render(request, "kfet/fournisseuredit.html", {'form' : form, 'instance' : object_to_manage.pk})


def homePians(request):
	#Récupération de la liste des PG débucquables
	list_pg_debucquable = list_pg()

	#Récupération des entités de l'utilisateur authentifié et de l'entité selectionnée
	if request.user.is_authenticated():
		current_user_group = request.user.groups.all().values_list('name')
		user_entity = entity.objects.filter(Q(name__in=current_user_group))
		entite=user_entity[0].name
		if request.GET.__contains__('entity'):
			entite=request.GET.__getitem__('entity')

	if (request.method == 'GET' or request.method == 'POST') and request.GET.__contains__('pg'):# or request.POST.__contains__('input_sent')):

		#Récupération du PG
		pg = request.GET.__getitem__('pg')
		fcd=str(pg.encode('utf-8')).lower().split(" / ")
		try:
			target = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
		except:
			#Render PG Vide
			if request.user.is_authenticated():
				return render(request, "kfet/homePians.html",{'list_pg_debucquable' : list_pg_debucquable,'user_entity' : user_entity, 'entity' : entite})
			return render(request, "kfet/homePians.html",{'list_pg_debucquable' : list_pg_debucquable})
		target_credit = target.credit
		target_header = ""
		if target.bucque != "" or target.fams != "":
			target_header += (target.bucque + " " + target.fams + " - ")
		target_header += (target.prenom + " " + target.nom)

		#Récupération de l'historique
		listmatch=getHisto(target.pk)

		if request.user.is_authenticated():

			#Récupération des produits selon l'entité active
			list_produit = list_product(entite)
			list_favorite_product = product.objects.filter(Q(associated_entity__name=entite) & Q(favorite = 1) & Q(enable = 1)).values_list('pk','name','price','shortcut').order_by('-pk')[:8]

			#Debucquage (sur transactionboulc) avec vérification d'autorisation d'entité
			if request.POST.__contains__('produit_id') :
				product_id = request.POST.__getitem__('produit_id')
				try:
					authortb=Client.objects.get(pk = request.user.pk)
					product_to_apply=product.objects.get(pk=product_id)
					product_price=product_to_apply.price
					product_name=product_to_apply.name
					entite_produit=product_to_apply.associated_entity
					if (request.user.groups.filter(name='can_negats').exists() or target_credit >= product_price) and request.user.groups.filter(name=entite_produit).exists(): #Vérification de l'entité
						vform = VirtualbucquageboulcForm()
						vform = vform.save(commit=False)
						vform.authortb=authortb
						vform.target=target
						vform.product_price=product_price
						vform.product_name=product_name
						vform.entite=entite_produit
						vform.save()
						var_stock(product_to_apply, "1", False)
						Client.debitpg(target,product_price)
						target_credit = target.credit
						listmatch=getHisto(target.pk)
						messages.success(request, u"Bucquage effectué")
					else:
						messages.error(request, u"Pas assez d'argent sur le compte cible")
				except:
					messages.error(request, "Ce produit n'existe pas...")

			#Render avec authentification et avec choix de PG
			return render(request, "kfet/homePians.html", {'pg' : pg, 'target_header' : target_header,'target_credit' : target_credit, 'list_pg_debucquable' : list_pg_debucquable, 'list_produit' : list_produit,'list_favorite_product' : list_favorite_product,'listmatch' : listmatch, 'user_entity' : user_entity, 'entity' : entite } )

		#Render sans authentification et avec choix de PG
		else:
			return render(request, "kfet/homePians.html", {'pg' : pg, 'target_header' : target_header,'target_credit' : target_credit,'list_pg_debucquable' : list_pg_debucquable, 'listmatch' : listmatch } )

	#Render accueil
	if request.user.is_authenticated():
		return render(request, "kfet/homePians.html",{'list_pg_debucquable' : list_pg_debucquable, 'user_entity' : user_entity, 'entity' : entite})
	else:
		return render(request, "kfet/homePians.html",{'list_pg_debucquable' : list_pg_debucquable})

@login_required
@user_passes_test(has_group_can_create_product)
def uploadfacture(request):
	entites = entity.objects.filter().values_list('name')
	#on récupère les entités rattachées à l'utilisateur
	liste_entites = []
	#on en crée une liste pour récupérer que le nom et les mettre en forme
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST':
		form = factureForm(request.POST, request.FILES)
		print form
		if form.is_valid():
			vform = VirtualfactureForm()
			vform = vform.save(commit=False)
			vform.titre = form.cleaned_data['titre']
			vform.price = form.cleaned_data['price']
			vform.date_facture = convertDate(form.cleaned_data['date_facture'])
			entityvalue = form.cleaned_data['associated_entity']
			vform.associated_entity = entity.objects.get(name = entityvalue.lower())
			vform.document=stockagefacture(document = request.FILES['document'])
			vform.save()
			messages.success(request, u"Upload réussi !")
			return redirect("kfet.views.uploadfacture")
		else :
			messages.error(request, u"Une erreur est survenue")
			return redirect("kfet.views.uploadfacture")
	else:
		form = factureForm()
	return render(request, "kfet/uploadfacture.html", {'liste_entites' : liste_entites,'form': form})



def cvisPians(request):
	#Récupération de la liste des PG débucquables
	list_pg_debucquable = list_pg()
	#Récupération des entités de l'utilisateur authentifié et de l'entité selectionnée
	if request.user.is_authenticated():
		current_user_group = request.user.groups.all().values_list('name')
		user_entity = entity.objects.filter(Q(name__in=current_user_group))
		entite=user_entity[0].name
		if request.GET.__contains__('entity'):
			entite=request.GET.__getitem__('entity')

	if (request.method == 'GET' or request.method == 'POST') and request.GET.__contains__('pg'):# or request.POST.__contains__('input_sent')):

		#Récupération du PG
		pg = request.GET.__getitem__('pg')
		fcd=str(pg.encode('utf-8')).lower().split(" / ")
		try:
			target = Client.objects.get(Q(nom__in=fcd) & Q(prenom__in=fcd))
		except:
			#Render PG Vide
			if request.user.is_authenticated():
				return render(request, "kfet/cvisPians.html",{'list_pg_debucquable' : list_pg_debucquable,'user_entity' : user_entity, 'entity' : entite})
			return render(request, "kfet/cvisPians.html",{'list_pg_debucquable' : list_pg_debucquable})
		target_credit = target.credit
		target_header = ""
		if target.bucque != "" or target.fams != "":
			target_header += (target.bucque + " " + target.fams + " - ")
		target_header += (target.prenom + " " + target.nom)

		#Récupération de l'historique
		listmatch=getHisto(target.pk)

		if request.user.is_authenticated():

			#Récupération des catégories
			categories = category.objects.filter(Q(entity__name=entite)).values_list('name').order_by('-name')
			liste_categories = []
			for categorie in categories:
				liste_categories.append(str(categorie[0].encode('utf-8')))

			#Récupération des produits selon l'entité active
			list_produit = list_product(entite)
			listmatch1 = product.objects.order_by('name').filter(Q(associated_entity__name="cvis"))
			list_produit_category =[]
			for elt in listmatch1:
				cat=(str(elt.associated_category))
				produit = [elt.pk, (elt.name).encode('utf-8')+" - "+str(elt.price)+'€', cat, elt.price]
				list_produit_category.append(produit)
			list_favorite_product = product.objects.filter(Q(associated_entity__name=entite) & Q(favorite = 1) & Q(enable = 1)).values_list('pk','name','price','shortcut').order_by('-pk')[:8]

			#Debucquage (sur transactionboulc) avec vérification d'autorisation d'entité
			if request.POST.__contains__('produit_id') :
				product_id = request.POST.__getitem__('produit_id')
				try:
					authortb=Client.objects.get(pk = request.user.pk)
					product_to_apply=product.objects.get(pk=product_id)
					product_price=product_to_apply.price
					product_name=product_to_apply.name
					entite_produit=product_to_apply.associated_entity
					if (request.user.groups.filter(name='can_negats').exists() or target_credit >= product_price) and request.user.groups.filter(name=entite_produit).exists(): #Vérification de l'entité
						vform = VirtualbucquageboulcForm()
						vform = vform.save(commit=False)
						vform.authortb=authortb
						vform.target=target
						vform.product_price=product_price
						vform.product_name=product_name
						vform.entite=entite_produit
						vform.save()
						var_stock(product_to_apply, "1", False)
						Client.debitpg(target,product_price)
						target_credit = target.credit
						messages.success(request, u"Bucquage effectué")
					else:
						messages.error(request, u"Pas assez d'argent sur le compte cible")
				except:
					messages.error(request, "Ce produit n'existe pas...")

			#Render avec authentification et avec choix de PG
			return render(request, "kfet/cvisPians.html", {'pg' : pg, 'target_header' : target_header,'target_credit' : target_credit, 'list_pg_debucquable' : list_pg_debucquable, 'list_produit' : list_produit, 'list_produit_category' : list_produit_category, 'list_favorite_product' : list_favorite_product,'listmatch' : listmatch, 'user_entity' : user_entity, 'entity' : entite, 'liste_categories' : liste_categories } )

		#Render sans authentification et avec choix de PG
		else:
			return render(request, "kfet/cvisPians.html", {'pg' : pg, 'target_header' : target_header,'target_credit' : target_credit,'list_pg_debucquable' : list_pg_debucquable, 'listmatch' : listmatch } )

	#Render accueil
	if request.user.is_authenticated():
		return render(request, "kfet/cvisPians.html",{'list_pg_debucquable' : list_pg_debucquable, 'user_entity' : user_entity, 'entity' : entite})
	else:
		return render(request, "kfet/cvisPians.html",{'list_pg_debucquable' : list_pg_debucquable})

@login_required
@user_passes_test(has_group_can_create_product)
def corrStock(request):
	entites = entity.objects.filter().values_list('name')
	liste_entites = []
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST':
		form = stockEditForm(request.POST)
		print form
		if form.is_valid():
			name = form.cleaned_data['name']
			varstock = form.cleaned_data['varstock']
			product_to_search=str((form.cleaned_data['name']).encode('utf-8')).lower().split(" / ")
			product_to_apply=product.objects.get(Q(name__in=product_to_search))
			var_stock(product_to_apply, varstock, True)
			if varstock == 0:
				messages.error(request, u"Il n'y a aucune variation de stock !")
				return render(request, "kfet/correctionStock.html")
			elif varstock > 0 :
				vform = VirtualapprosForm()
				vform = vform.save(commit=False)
				vform.num_facture = "Correction"
				vform.entity =product_to_apply.associated_entity
				vform.date = date.today()
				vform.product_price = 0
				vform.product = product_to_apply
				vform.quantity = varstock
				vform.save()
				messages.success(request, u"Stock corrigé")
				return render(request, "kfet/correctionStock.html")
			else:
				for i in range (-varstock):
					vform = VirtualbucquageboulcForm()
					vform = vform.save(commit=False)
					vform.authortb=Client.objects.get(Q(id=15))
					vform.target=Client.objects.get(Q(id=15))
					vform.product_price=0
					vform.product_name=(product_to_search)[0]
					vform.entite=(product.objects.filter(Q(name__in=product_to_search)).values_list('associated_entity__name'))[0][0]
					vform.save()
				messages.success(request, u"Stock corrigé")
				return render(request, "kfet/correctionStock.html")
		else:
			messages.error(request, u"Une erreur est survenue")
			return render(request, "kfet/correctionStock.html")
	else:
		form = productForm()
		return render(request, "kfet/correctionStock.html")

@login_required
# @user_passes_test(has_group_grippserie_boquette)
def entityaccounting(request):
	entites = entity.objects.filter().values_list('name')  #on récupère les entités rattachées à l'utilisateur
	liste_entites = [] #on en crée une liste pour récupérer que le nom et les mettre en forme
	for entite in entites:
		liste_entites.append(str(entite[0].encode('utf-8')))
	if request.method == 'POST':
		pass
	return render(request, "kfet/entityaccounting.html",{'liste_entites' : liste_entites})
