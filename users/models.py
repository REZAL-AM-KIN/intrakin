#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.core import exceptions
#from kfet.models import entity

import datetime
import hashlib
import base64
import os

# Create your models here.

class   radreply(models.Model):
	username = models.CharField(max_length = 17)
	attribute = models.CharField(max_length = 254, default = 'WISPR-Bandwidth-Max-Down')
	op = models.CharField(max_length = 2, default = '=')
	value = models.CharField(max_length = 254, default = '960000')

	class Meta:
		db_table = 'radreply'

class   radcheck(models.Model):
	username = models.CharField(max_length = 17)
	attribute = models.CharField(max_length = 64, default = 'ClearText-Password')
	op = models.CharField(max_length = 2, default = ':=')
	value = models.CharField(max_length = 64, default = 'authok')

	class Meta:
		db_table = 'radcheck'

class Client(User):
	nom = models.CharField(max_length = 64)
	prenom = models.CharField(max_length = 64)
	chambre = models.CharField(max_length = 5)
	mail = models.EmailField(max_length = 254)
	phone = models.CharField(max_length = 10)
	bucque = models.CharField(blank = True, max_length = 254)
	fams = models.CharField(blank = True, max_length = 254, verbose_name = u"Fam's")
	proms = models.CharField(blank = True, max_length = 254, verbose_name = u"Prom's")
        date_fin_abo = models.DateField(default=datetime.date.today)
	has_rezal = models.BooleanField(default = False)
	is_gadz = models.BooleanField(default = False)
	is_conscrit = models.BooleanField(default = False)
	is_debucquable = models.BooleanField(default = False)
	credit = models.DecimalField(max_digits=5, decimal_places=2, default = 0, blank = True)
	UID_RFID = models.CharField(max_length = 64, null = True, default = None)

	def save(self, *args, **kwargs):
		super(Client, self).save(*args, **kwargs)
		b = device.objects.filter(publisher = self.pk)
		if b != []:
			if not self.has_rezal:
				for i in b:
					i.activated = False
					i.save()
			else:
				for i in b:
					if i.accepted:
						i.activated = True
						i.save()
	
	def __unicode__(self):
		return self.username
		
	def creditpg(self,x):
		self.credit += x
        	self.save()
		
	def debitpg(self,x):
		self.credit -= x
		self.save()

class device(models.Model):
	nom = models.CharField("Nom", max_length = 64)
	mac = models.CharField(max_length = 17)
	publisher = models.ForeignKey('Client')
	accepted = models.BooleanField(default = False)
	activated = models.BooleanField(default = True)
	
	def save(self, *args, **kwargs):
		super(device, self).save(*args, **kwargs)
		b = Client.objects.get(pk = self.publisher.pk)
		
		if b.has_rezal and self.accepted == True and self.activated == True:
			tmp, created = radcheck.objects.get_or_create(username = self.mac, attribute = "ClearText-Password", op = ":=", value = "authok")
		else:
			try:
				tmp = radcheck.objects.filter(username = self.mac)
				tmp.all().delete()
				tmp = radreply.objects.filter(username = self.mac)
				tmp.all().delete()
			except (exceptions.ObjectDoesNotExist, exceptions.MultipleObjectsReturned):
				return
			
	def mdt_on(self, x):
		b = Client.objects.get(pk = self.publisher.pk)
		if b.has_rezal and self.accepted == True and self.activated == True and b.is_conscrit:
			tmp, created = radreply.objects.get_or_create(username = self.mac, attribute = "WISPr-Bandwidth-Max-Down", op = "=", value = x)
			tmp, created = radreply.objects.get_or_create(username = self.mac, attribute = "WISPr-Bandwidth-Max-Up", op = "=", value = int(x)//2)

