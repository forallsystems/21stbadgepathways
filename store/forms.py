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
    district_id = forms.CharField(required=True, widget=forms.HiddenInput)
    name = forms.CharField(max_length=256, label='Name')
    description = forms.CharField(label='Description', widget=forms.Textarea,required=False)
    points = forms.IntegerField(label='Points', min_value=0)
    inventory = forms.IntegerField(label='Inventory', min_value=0)
    organization = forms.MultipleChoiceField(label='Assigned School(s)',
                                             required=False,
                                             help_text='<span style="font-size:.9em;"><i>Hold Ctrl/Cmd to select multiple schools.</i></span>')

    def __init__(self,*args,**kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        district_id = ''
        if(kwargs.has_key('initial')):
            district_id = kwargs['initial']['district_id']
        else:
            district_id = self.data['district_id']

        schoolList = []    
        for org in Organization.get_schools(district_id):
            schoolList.append((org.id,org.__unicode__()))
            
        self.fields['organization'].choices =  schoolList