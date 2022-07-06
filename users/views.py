#-*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from users.models import Client, device, radcheck, radreply
from django.contrib import messages
from users.forms import LoginForm, UserInscriptionForm, GadzEditForm, UserEditForm, MacForm, mdtForm, ContactForm, checkForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.core import exceptions
from intra.pattern_decorators import hasrezal_required
from django.db.models import Q, Count
from django.core.mail import send_mail
from random import randint
from itertools import chain

# Create your views here.

def cercle(request):
	return render(request,"users/cercle.html")

def loginPage(request):
	if request.user.is_authenticated():
		return redirect("users.views.statutpage")
	form = generalLogin(request)
	if form == None:
		return redirect("users.views.statutpage")
	return render(request, "users/login.html")

def loginPagePians(request):
	if request.user.is_authenticated():
		return redirect("kfet.views.homePians")
	form = generalLogin(request)
	if form == None:
		return redirect("kfet.views.homePians")
	return render(request, "users/login.html")

def loginPagecPians(request):
	if request.user.is_authenticated():
		return redirect("kfet.views.cvisPians")
	form = generalcLogin(request)
	if form == None:
		return redirect("kfet.views.cvisPians")
	return render(request, "users/login.html")


def generalLogin(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			password = form.cleaned_data['password']
			user = authenticate(username = user, password = password)
			if user and user.is_active:
				login(request, user)
				messages.success(request, u"Connexion réussie !")
				c = Client.objects.get(pk = user.pk)
				if c.is_gadz and not c.bucque:
					messages.error(request, u"Pense à rajouter ta bucque dans les paramètres de ton compte !")
				return None
			elif user and not user.is_active:
				messages.error(request, u"Votre compte est désactivé, contactez le support")
				return None
			else:
				logout(request)
				messages.error(request, u"Une erreur est survenue lors de la connexion : mauvais identifiants")
				if request.path == "/loginPians/":
					return redirect("users.views.loginPagePians")
				elif request.path == "/logincPians/":
					return redirect("users.views.loginPagecPians")
				else:
					return redirect("users.views.loginPage")
		else:
			messages.error(request, u"Une erreur est survenue lors de la connexion : champs incorrectement remplis")
			if request.path == "/loginPians/":
				return redirect("users.views.loginPagePians")
			elif request.path == "/logincPians/":
				return redirect("users.views.loginPagecPians")
			else:
				return redirect("users.views.loginPage")
	else:
		form = LoginForm()
	return form

def generalcLogin(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			password = form.cleaned_data['password']
			user = authenticate(username = user, password = password)
			if user and user.is_active:
				login(request, user)
				messages.success(request, u"Connexion réussie !")
				c = Client.objects.get(pk = user.pk)
				if c.is_gadz and not c.bucque:
					messages.error(request, u"Pense à rajouter ta bucque dans les paramètres de ton compte !")
				return None
			elif user and not user.is_active:
				messages.error(request, u"Votre compte est désactivé, contactez le support")
				return None
			else:
				logout(request)
				messages.error(request, u"Une erreur est survenue lors de la connexion : mauvais identifiants")
				if request.path == "/loginPians/":
					return redirect("users.views.loginPagePians")
				elif request.path == "/logincPians/":
					return redirect("users.views.loginPagecPians")
				else:
					return redirect("users.views.loginPage")
		else:
			messages.error(request, u"Une erreur est survenue lors de la connexion : champs incorrectement remplis")
			if request.path == "/logincPians/":
				return redirect("users.views.loginPagecPians")
			else:
				return redirect("users.views.loginPage")
	else:
		form = LoginForm()
	return form


def inscription(request):
	if request.method == 'POST':
		form = UserInscriptionForm(request.POST)
		if form.is_valid():
			user = form.save(commit = False)
			user.set_password(user.password)
			user.email = user.mail
			user.save()
			messages.success(request, u"Création du compte réussie !")
			return redirect("users.views.index")
		else:
			messages.error(request, u"Une erreur est survenue lors de la création du compte")
	else:
		form = UserInscriptionForm()
	return render(request, "users/inscription.html", {'form' : form })


def index(request):
	return render(request, "users/index.html")

@login_required
def settings(request):
	try:
		gadz = Client.objects.get(username = request.user.username)
		a = 0
		if gadz.is_gadz:
			f = GadzEditForm
			a = gadz
		else:
			f = UserEditForm
			a = gadz
	except (AttributeError, exceptions.ObjectDoesNotExist):
		f = UserEditForm
		a = request.user
	if request.method == 'POST':
		form = f(request.POST, instance =a)
		if form.is_valid():
			user = form.save(commit = False)
			user.email = user.mail
			user.save()
			form.save()
			messages.success(request, u"Modification(s) réussie(s)")
			return redirect("users.views.settings")
		else:
			messages.error(request, form.cleaned_data())
			messages.error(request, u"Une erreur est survenue lors de la modification")
			return redirect("users.views.settings")
	else:
		form = f(instance = a)
	return render(request, 'users/settings.html', {'form' : form})


def has_rezal_check(user):
	b = Client.objects.filter(has_rezal = True)
	c = Client.objects.get(pk = user.pk)
	h = False
	if c in b:
		h = True
	return h

@login_required
@user_passes_test(has_rezal_check)
def add_mac(request):
	if request.method == 'POST':
		form = MacForm(request.POST)
		if form.is_valid():
			form = form.save(commit = False)
			b = Client.objects.get(pk = request.user.pk)
			form.publisher = b
			mactomanage = form.mac
			mactoapply = mactomanage.lower()
			if len(mactoapply) != 17:
				messages.error(request, u"Format d'adresse incorrect")
				return redirect("users.views.add_mac")
			form.mac = mactoapply
			nbofmacused = device.objects.filter(publisher = request.user.pk).count()
			if nbofmacused == 0:
				form.accepted = True
				form.activated = True
				form.save()
				return render(request, "users/statutpage.html", {'verif' : "OK" })
			else:
				form.accepted = False
				form.activated = True
				form.save()
				messages.success(request, u"Adresse MAC en attente d'approbation")
				return redirect("users.views.show_mac")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("users.views.show_mac")
	else:
		form = MacForm()
	return render(request, 'users/add_mac.html', {'form' : form})

@login_required
@user_passes_test(has_rezal_check)
def show_mac(request):
	b = Client.objects.get(pk = request.user.pk)
	listmac = device.objects.filter(Q(publisher = b) & Q(activated = True)).order_by('-pk').values_list('nom','mac', 'accepted')
	if request.method == 'POST':
		req_nbr = request.POST.__getitem__('mac_nbr')
		instance_to_pass = device.objects.filter(Q(publisher = b) & Q(activated = True)).order_by('-pk')[int(req_nbr)]

		if getattr(instance_to_pass, 'mac') == listmac[int(req_nbr)][1]:
			instance_to_pass.activated = False
			instance_to_pass.save()
			messages.success(request, u"Adresse MAC désactivée")
			return redirect("users.views.show_mac")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("users.views.show_mac")

	return render(request, 'users/show_mac.html', {'listmac' : listmac })

@login_required
@staff_member_required
def macapprobation(request):
	#list_to_approve = device.objects.filter(Q(accepted = False) & Q(activated = True)).order_by('pk').values_list('publisher__nom','publisher__username','nom','mac')
	list_to_approve=[]
	query1 = device.objects.filter(Q(accepted = False) & Q(activated = True)).order_by('-pk').values_list('publisher','publisher__nom','publisher__username','nom','mac')

	for i in query1:
		pub = i[0]
		query2 = device.objects.filter(Q(accepted = True) & Q(activated = True) &Q(publisher =pub)).count()
		list_to_approve.append([i[1],i[2],query2, i[3], i[4]])
	if request.method == 'POST':
		if request.POST.__contains__('accept_mac'):
			req_nbr = request.POST.__getitem__('accept_mac')
			instance_to_pass = device.objects.filter(Q(accepted = False) & Q(activated = True)).order_by('-pk')[int(req_nbr)]
			instance_to_pass.accepted = True
			instance_to_pass.save()
			messages.success(request, u"Adresse MAC acceptée")
			return redirect("users.views.macapprobation")
		elif request.POST.__contains__('delete_mac'):
			req_nbr = request.POST.__getitem__('delete_mac')
			instance_to_pass = device.objects.filter(Q(accepted = False) & Q(activated = True)).order_by('-pk')[int(req_nbr)]
			if getattr(instance_to_pass, 'mac') == list_to_approve[int(req_nbr)][4]:
				instance_to_pass.activated = False
				instance_to_pass.save()
				messages.success(request, u"Adresse MAC désactivée")
				return redirect("users.views.macapprobation")
			else:
				messages.error(request, u"Une erreur est survenue")
				return redirect("users.views.macapprobation")
	return render(request, "users/macapprobation.html", {'listmac' : list_to_approve})

@login_required
@staff_member_required
def macdeletion(request):
	#list_to_delete = device.objects.filter(Q(accepted = True) & Q(activated = True)).order_by('-pk').values_list('publisher__nom','publisher__username','nom','mac')	# "-pk" pour inverser l'ordre
	list_to_delete=[]
	query1 = device.objects.filter(Q(accepted = True) & Q(activated = True)).order_by('-pk').values_list('publisher','publisher__nom','publisher__username','nom','mac')

	for i in query1:
		pub = i[0]
		query2 = device.objects.filter(Q(accepted = True) & Q(activated = True) &Q(publisher =pub)).count()
		list_to_delete.append([i[1],i[2],query2, i[3], i[4]])

	if request.method == 'POST':
		req_nbr = request.POST.__getitem__('mac_nbr')
		instance_to_pass = device.objects.filter(Q(accepted = True) & Q(activated = True)).order_by('-pk')[int(req_nbr)]

		if getattr(instance_to_pass, 'mac') == list_to_delete[int(req_nbr)][4]:
			instance_to_pass.activated = False
			instance_to_pass.save()
			messages.success(request, u"Adresse MAC désactivée")
			return redirect("users.views.macdeletion")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("users.views.macdeletion")
	return render(request, "users/macdeletion.html", {'listmac' : list_to_delete})

def contactform(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			mail = form.cleaned_data['mail']
			subject = 'Formulaire de Contact Intra - ' + form.cleaned_data['subject']
			body = form.cleaned_data['body']
			send_mail(subject,"Adresse mail du demandeur : "+mail+"\n \n \n"+body,'support@rezal.fr',['support@rezal.fr', mail],fail_silently=False,)
			messages.success(request, u"Demande envoyée, une copie vous a également été envoyée à "+mail+". (Souvent dans vos SPAMS.")
			return redirect("users.views.index")
		else:
			messages.error(request, u"Une erreur est survenue")
			return redirect("users.views.contactform")
	else :
		form = ContactForm()
	return render(request, "users/contactform.html",  {'form' : form})

@login_required
@staff_member_required
def admincontrols(request):
	number_to_fill=randint(0,1000)
	if request.method =='POST':
		if request.POST.__contains__('apply_mdt'):
			form = mdtForm(request.POST)
			if form.is_valid():
				limitation = form.cleaned_data['limitation']
				devices_to_manage = device.objects.filter(Q(accepted = True) & Q(activated = True))
				for device_to_manage in devices_to_manage:
					device.mdt_on(device_to_manage, limitation)
				messages.warning(request, u"MDT appliquée sur les conscrits !")
				return redirect("users.views.admincontrols")
			else:
				messages.error(request, u"Une erreur est survenue")
				return redirect("users.views.admincontrols")
		elif request.POST.__contains__('off_mdt'):
			tmp = radreply.objects.all()
			tmp.all().delete()
			messages.success(request, u"MDT désactivée")
			return redirect("users.views.admincontrols")
		elif request.POST.__contains__('gadz_pass'):
			conscrit_to_bapts = Client.objects.filter(Q(is_conscrit = True))
			form = checkForm(request.POST)
			if form.is_valid():
				number_to_valid = form.cleaned_data['numbercheck']
				number_to_fill = request.POST.__getitem__('gadz_pass')
				if str(number_to_valid) == str(number_to_fill):
					for conscrit in conscrit_to_bapts:
						conscrit.is_gadz = True
						conscrit.is_conscrit = False
						conscrit.save()
					messages.success(request, u"Tous les conscrits ont maintenant accès aux modules Gadz !")
					return redirect("users.views.admincontrols")
				else:
					messages.warning(request, u"Le nombre ne correspond pas")
					return redirect("users.views.admincontrols")
			else:
				messages.error(request, u"Une erreur est survenue")
				return redirect("users.views.admincontrols")

		elif request.POST.__contains__('renew_rezal'):
			users_to_disable = Client.objects.filter(Q(has_rezal = True) & Q(is_active = True))
			form = checkForm(request.POST)
			if form.is_valid():
				number_to_valid = form.cleaned_data['numbercheck']
				number_to_fill = request.POST.__getitem__('renew_rezal')
				if str(number_to_valid) == str(number_to_fill):
					for user_to_disable in users_to_disable:
						user_to_disable.has_rezal = False
						user_to_disable.save()
					messages.success(request, u"L'accès au Rézal est maintenant coupé pour tous les comptes")
					return redirect("users.views.admincontrols")
				else:
					messages.warning(request, u"Le nombre ne correspond pas")
					return redirect("users.views.admincontrols")
			else:
				messages.error(request, u"Une erreur est survenue")
				return redirect("users.views.admincontrols")
	else:
		form = mdtForm()
	return render(request, "users/admincontrols.html", {'numbercheck' : number_to_fill})

def about(request):
	device_count=device.objects.filter(activated = True).count()
	user_count=Client.objects.all().count()
	return render(request, "users/about.html", {'device_count' : device_count, 'user_count':user_count })

@login_required
def statutpage(request):
	device_check = device.objects.filter(publisher = request.user.pk).count()
	c = Client.objects.get(pk = request.user.pk)
	if device_check == 0:
		verif = "KO"
	else:
		verif = "OK"
	if verif == "OK" and c.has_rezal:
		return redirect("users.views.index")
	return render(request, "users/statutpage.html", {'verif' : verif })
