#-*- coding: utf-8 -*-
from django import forms
from elec.models import item, operation, items_list

class itemForm(forms.Form):
	name = forms.CharField()
	brand = forms.CharField()
	ref = forms.CharField()
	kind = forms.CharField()
	purchase_date = forms.CharField(required=False)
	purchase_value = forms.DecimalField(required=False)
	quantity=forms.IntegerField(required=False)
	comment = forms.CharField(required=False)
	state = forms.CharField(required=False)
	usual_stockage = forms.CharField()
	current_place = forms.CharField()
	
	
class VirtualitemForm (forms.ModelForm):
	class Meta:
		model = item
		fields = ['name','brand','ref','associated_kind','purchase_date','purchase_value','quantity','comment','state','usual_stockage','current_place']
		
class entree_sortie_matosForm(forms.ModelForm):
	class Meta:
		model = operation
		fields = ['name','comment','items','publisher','from_place','to_place']
	items = forms.ModelMultipleChoiceField(queryset=operation.objects.all())
	def __init__(self, *args, **kwargs):
		if kwargs.get('instance'):
			initial = kwargs.setdefault('initial', {})
			initial['items'] = [t.pk for t in kwargs['instance'].Operation_set.all()]
		forms.ModelForm.__init__(self, *args, **kwargs)
	def save(self, commit=True):
		instance = forms.ModelForm.save(self, False)
		old_save_m2m = self.save_m2m
		def save_m2m():
			old_save_m2m()
			instance.Operation_set.clear()
			for element in self.cleaned_data['item']:
				instance.Operation_set.add(element)
		self.save_m2m = save_m2m
		if commit:
			instance.save()
			self.save_m2m()
		return instance
		
class add_item_to_operationForm(forms.Form):
	item_id = forms.CharField()
	quantity=forms.IntegerField()
	items_to_manage_id = forms.CharField()
	items_to_manage_quantity = forms.CharField()

	
