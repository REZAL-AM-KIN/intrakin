#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core import exceptions
from users.models import Client

# Create your models here.

class transactionvp(models.Model):
	authortvp=models.CharField(max_length=200, default="VP")
	target=models.ForeignKey('users.Client', related_name='transactionvp_target')
	date=models.DateTimeField(auto_now_add=True, auto_now=False)
	product_price=models.DecimalField(max_digits=5, decimal_places=2)
	product_name=models.CharField(max_length=200)
	quantity=models.PositiveIntegerField(default=1)
	enable=models.BooleanField(default=True)
	entite=models.CharField(max_length=200, default='Kfet')
	exported=models.BooleanField(default=False)

	def __unicode__(self):
		return self.product_name

class transactionboulc(models.Model):
	authortb=models.ForeignKey('users.Client', related_name='transactionboulc_authortb')
	target=models.ForeignKey('users.Client', related_name='transactionboulc_target')
	date=models.DateTimeField(auto_now_add=True, auto_now=False)
	product_price=models.DecimalField(max_digits=5, decimal_places=2)
	product_name=models.CharField(max_length=200)
	quantity=models.PositiveIntegerField(default=1)
	accepted=models.BooleanField(default=True)
	entite=models.CharField(max_length=200, default='Kfet')
	exported=models.BooleanField(default=False)

	def __unicode__(self):
		return self.product_name

class transactionpg(models.Model):
	source=models.ForeignKey('users.Client', related_name='transactionpg_source')
	target=models.ForeignKey('users.Client', related_name='transactionpg_target')
	date=models.DateTimeField(auto_now_add=True, auto_now=False)
	amount=models.DecimalField(max_digits=5, decimal_places=2)
	description=models.CharField(max_length=200)
	accepted=models.BooleanField(default=False)

	def __unicode__(self):
		return self.description

class cashinput(models.Model):
	authorci=models.ForeignKey('users.Client', related_name='cashinput_authorci')
	target=models.ForeignKey('users.Client', related_name='cashinput_target')
	date=models.DateTimeField(auto_now_add=True, auto_now=False)
	amount=models.DecimalField(max_digits=5, decimal_places=2)
	method=models.ForeignKey('inputmethod')

class inputmethod(models.Model):
	name=models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

class product(models.Model):
	name=models.CharField(max_length=200)
	price=models.DecimalField(max_digits=5, decimal_places=2)
	associated_entity=models.ForeignKey('entity')
	associated_category=models.ForeignKey('category', null=True)
	shortcut=models.CharField(max_length=5, unique=True)
	instant=models.BooleanField(default=1)
	stock=models.PositiveIntegerField(default=None,null=True)
	favorite=models.PositiveIntegerField(default=0)
	enable=models.PositiveIntegerField(default=1)

	def __unicode__(self):
		return self.name

class category(models.Model):
	name=models.CharField(max_length=200)
	entity=models.ForeignKey('kfet.entity', related_name='category_entity', default=3)
	
	def __unicode__(self):
		return self.name

class entity(models.Model):
	name=models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

class fournisseur(models.Model):
	name=models.CharField(max_length=200)
	tel=models.CharField(max_length=200, null=True)
	adress=models.CharField(max_length=200, null=True)
	mail=models.CharField(max_length=200, null=True)
	remark=models.CharField(max_length=400, null=True)
	associated_entity=models.ForeignKey('entity', default=3)
	
	
	def __unicode__(self):
		return self.name

class appros(models.Model):
	num_facture=models.CharField(max_length=200)
	entity=models.ForeignKey('kfet.entity', related_name='appros_entity')
	date=models.DateField(default=None)
	product=models.ForeignKey('kfet.product', related_name='appros_product')
	product_price=models.DecimalField(max_digits=5, decimal_places=2)
	quantity=models.PositiveIntegerField(default=1)
	enable=models.PositiveIntegerField(default=1)

	def __unicode__(self):
		return str(self.id)

class cartemetro(models.Model):
	publisher = models.ForeignKey('users.Client', related_name='cartemetro_publisher')
	desired_date=models.DateTimeField(default=None)
	associated_entity=models.ForeignKey('entity')
	accepted=models.CharField(default=None,null=True,max_length=10)
	decision_by=models.ForeignKey('users.Client', default=None, related_name='cartemetro_decision_by',null=True)
	decision_date=models.DateTimeField(default=None,null=True)
	description=models.CharField(default=None,null=True,max_length=200)
	
	def __unicode__(self):
		return str(self.id)
		
class stockagefacture(models.Model):
	titre = models.CharField(max_length=255)
	associated_entity=models.ForeignKey('entity')
	upload_date=models.DateTimeField(auto_now_add=True, auto_now=False)
	date_facture=models.DateField()
	price=models.DecimalField(max_digits=10, decimal_places=2)
	document = models.FileField(upload_to='factures/', null=True)
	publisher = models.ForeignKey('users.Client', related_name='stockagefacture_publisher')
	
	def __unicode__(self):
		return str(self.id)
	
class entity_accounting(models.Model):
	date_operation = models.DateTimeField(auto_now_add=True, auto_now=False)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	associated_entity=models.ForeignKey('entity',default=1)
	title = models.CharField(max_length=255)
	ref = models.CharField(max_length=255)
	real_account_ref = models.CharField(max_length=255)
	submitted_by = models.ForeignKey('users.Client', related_name='entityaccounting_submitted_by')
	approved_by = models.ForeignKey('users.Client', related_name='entityaccounting_approved_by',null=True)
	associated_bill = models.ForeignKey('kfet.stockagefacture', null=True)
	#test = models.CharField(max_length=255)
	#test2 = models.CharField(max_length=255)
	
	def __unicode__(self):
		return str(self.id)