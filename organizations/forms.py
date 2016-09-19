from django import forms
from django.contrib.auth.models import User
from bootstrap.forms import BootstrapForm, Fieldset
from organizations.models import *
from badges.models import *

class SchoolForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    name = forms.CharField(max_length=256, label='School Name')
    organization_id = forms.CharField(max_length=256, label='School ID')
    
    enable_store = forms.BooleanField(label='Enable Points Store?', required=False)
    enable_custom_login = forms.BooleanField(label='Allow School Admin to Customize Site?', required=False)
    
    login_url = forms.CharField(max_length=256, label='Login Page URL:', required=True)
    
    def clean(self):
        
        cleaned_data = super(BootstrapForm, self).clean()
        login_url =  cleaned_data.get('login_url')
        id = cleaned_data.get('id')

        for ss in Organization_Settings.objects.filter(deleted=0, login_url = login_url):
            if ss.organization_id != id:
                raise forms.ValidationError("This URL is already being used.")
        
       
               
        return cleaned_data
    
class SchoolSettingsForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    
    login_url = forms.CharField(max_length=256, label='Login Page URL:', required=True)
    
    primary_logo = forms.ImageField(label='Logo Image:', required=False, error_messages = {'invalid':"Image files only"}, widget=forms.FileInput)
    
    login_text = forms.CharField(label='Login Page Welcome Text:', widget=forms.Textarea,required=False)
    
    header_color = forms.CharField(label='Header Color:', max_length=7, required=True) 
    background_color = forms.CharField(label='Background Color:', max_length=7, required=True) 
    text_color = forms.CharField(label='Text Color:', max_length=7, required=True) 
    
    login_text_background_color = forms.CharField(label='Welcome Text Background Color:', max_length=7,  required=True) 
    login_text_color = forms.CharField(label='Welcome Text Color:', max_length=7, required=True) 
    
    