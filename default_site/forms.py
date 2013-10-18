from django import forms
from django.contrib.auth.models import User
from bootstrap.forms import BootstrapForm, Fieldset
from organizations.models import *
from badges.models import *
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):    
    username = forms.CharField(label=("Username"), max_length=255)
    


    


    