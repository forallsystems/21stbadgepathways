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
   