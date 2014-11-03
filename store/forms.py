from django import forms
from django.contrib.auth.models import User
from bootstrap.forms import BootstrapForm, Fieldset
from organizations.models import *

class VendorForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(max_length=256, label='Name')
    image  = forms.ImageField(label='Logo', required=False)
    
class ItemForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(max_length=256, label='Name')
    image  = forms.ImageField(label='Image', required=False)
    description = forms.CharField(label='Description', widget=forms.Textarea,required=False)
    points = forms.IntegerField(label='Points', min_value=0)
    inventory = forms.IntegerField(label='Inventory', min_value=0)
