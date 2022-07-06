from __future__ import unicode_literals

from django.db import models
from django.core import exceptions
from users.models import Client

# Create your models here.

class item(models.Model):
	name = models.CharField(max_length = 254)
	brand = models.CharField(max_length = 254)
	ref = models.CharField(max_length = 254, unique=True)
	associated_kind=models.ForeignKey('kind')
	purchase_date = models.DateField(default=None,null=True)
	purchase_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	quantity=models.PositiveIntegerField(default=1)
	comment = models.CharField(max_length = 2000, null=True)
	state = models.CharField(max_length = 200, null=True)
	usual_stockage = models.ForeignKey('place',null=True)
	current_place = models.ForeignKey('place',null=True, related_name = 'item_current_place')
	
	def __unicode__(self):
		return str(self.id)
	
class kind(models.Model):
	name=models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name

class place(models.Model):
	name=models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.name
		
class operation(models.Model):
	name = models.CharField(max_length=200)
	date = models.DateTimeField(auto_now_add=True, auto_now=False)
	comment = models.CharField(max_length=200)
	items = models.ManyToManyField('item', through = 'items_list')
	publisher = models.ForeignKey('users.Client', related_name='operation_publisher')
	from_place = models.ForeignKey('place',null=True)
	to_place = models.ForeignKey('place',null=True, related_name = 'operation_to_place')
	
	
	def __unicode__(self):
		return str(self.id)

class items_list(models.Model):
	operation = models.ForeignKey(operation, on_delete=models.CASCADE)
	item = models.ForeignKey(item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	#test = models.IntegerField(default=1)
