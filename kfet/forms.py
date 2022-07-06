#-*- coding: utf-8 -*-
from django import forms
from kfet.models import transactionpg, cashinput, transactionboulc, product, cartemetro, fournisseur, appros, stockagefacture

class transactionpgForm(forms.Form):
	pg = forms.CharField()
	amount = forms.DecimalField()
	description = forms.CharField()

class VirtualtransactionpgForm(forms.ModelForm):
	class Meta:
		model = transactionpg
		fields = ['source','target','amount','description']
		
class strpgForm(forms.ModelForm):
	class Meta:
		model = transactionpg
		fields = ['source', 'amount', 'description']

class remiseNatureForm(forms.Form):
	pg = forms.CharField()
	amount = forms.DecimalField()

class cashinputForm(forms.Form):
	CHOICES = (('CB','CB'),('Espèces','Espèces'),('Chèque','Chèque'),('Remise Nature','Remise Nature'),)
	pg = forms.CharField()
	amount = forms.DecimalField()
	method = forms.CharField()

class VirtualcashinputForm(forms.ModelForm):
	class Meta:
		model = cashinput
		fields = ['authorci','target','amount','method']
		
class seuilpgForm(forms.Form):
	seuil = forms.DecimalField()
	proms = forms.CharField()

class histopgForm(forms.Form):
	pg = forms.CharField()
	
class bucquageboulcForm(forms.Form):
	pg = forms.CharField()
	prod = forms.CharField()
	
class VirtualbucquageboulcForm(forms.ModelForm):
	class Meta:
		model = transactionboulc
		fields = ['authortb', 'target','product_price','product_name','entite']
		
class VirtualproductForm(forms.ModelForm):
	class Meta:
		model = product
		fields = ['name','price','associated_category','associated_entity', 'shortcut','stock','favorite','enable']
		
class productForm(forms.Form):
	name = forms.CharField()
	price = forms.DecimalField()
	category = forms.CharField(required=False)
	entity = forms.CharField()
	shortcut = forms.CharField()
	stock = forms.DecimalField(required=False)
	favorite = forms.IntegerField(required=False)
	enable = forms.IntegerField(required=False)
	
class VirtualreservationCarteMetroForm(forms.ModelForm): #formulaire pour remplir la base de données
	class Meta:
		model = cartemetro #table de la base de données associée
		fields = ['publisher','associated_entity','desired_date','description'] #colonne que je veux éditer

class reservationCarteMetroForm(forms.Form): #formulaire pour l'interaction avec le site
	associated_entity = forms.CharField() #liste des donnée à remplir par l'utilisateur
	date_desired = forms.CharField()
	description=forms.CharField(required=False)
	form_id=forms.CharField()

class VirtualfactureForm(forms.ModelForm):
    class Meta:
        model = stockagefacture
        fields = ['titre','date_facture','price','document', 'associated_entity']

class factureForm(forms.Form):
	associated_entity = forms.CharField() #liste des donnée à remplir par l'utilisateur
	date_facture = forms.CharField()
	titre=forms.CharField()
	price=forms.DecimalField()
	document=forms.FileField()
	
class productEditForm(forms.ModelForm):
	stock = forms.DecimalField(required=False)
	class Meta:
		model = product
		fields = ['name', 'price','shortcut', 'stock']
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(productEditForm, self).__init__(*args, **kwargs)

		
class bucquageboulcgrForm(forms.Form):
	pgs = forms.CharField()
	prod = forms.CharField()
	
class approsForm(forms.Form):
	num_facture=forms.CharField()
	entity=forms.CharField()
	date=forms.CharField()
	product=forms.CharField()
	product_price=forms.DecimalField()
	quantity=forms.DecimalField()

class VirtualapprosForm(forms.ModelForm):
	class Meta:
		model = appros
		fields = ['num_facture', 'entity', 'date', 'product', 'product_price', 'quantity']

class approEditForm(forms.ModelForm):
	class Meta :
		model = appros
		fields = ['num_facture', 'date', 'product_price']
		def __init__(self, *args, **kwargs):
			self.request = kwargs.pop('request', None)
			super(approEditForm, self).__init__(*args, **kwargs)

class fournisseurForm(forms.Form):
	name=forms.CharField()
	tel=forms.CharField(required=False)
	adress=forms.CharField(required=False)
	mail=forms.CharField(required=False)
	remark=forms.CharField(required=False)
	entity = forms.CharField()

class VirtualfournisseurForm(forms.ModelForm):
	class Meta:
		model = fournisseur
		fields = ['name', 'tel', 'adress', 'mail', 'remark']

class fournisseurEditForm(forms.ModelForm):
	tel = forms.CharField(required=False)
	adress = forms.CharField(required=False)
	mail = forms.CharField(required=False)
	remark = forms.CharField(required=False)
	class Meta:
		model = fournisseur
		fields = ['name', 'tel', 'adress','mail', 'remark']
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(fournisseurEditForm, self).__init__(*args, **kwargs)

class stockEditForm(forms.Form):
	name=forms.CharField()
	varstock = forms.DecimalField()