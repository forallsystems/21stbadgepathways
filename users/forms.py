from django import forms
from django.contrib.auth.models import User
from bootstrap.forms import BootstrapForm, Fieldset
from organizations.models import *
from django.contrib.auth.forms import AuthenticationForm

class AccountForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    parent_organization_id = forms.CharField(required=False, widget=forms.HiddenInput)
    first_name = forms.CharField(max_length=256, label='First Name')
    last_name = forms.CharField(max_length=256, label='Last Name')
    username = forms.CharField(required=True, max_length=75, label='Username')
    original_username= forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(required=False, max_length=75, label='Email Address')
    original_email= forms.CharField(required=False, widget=forms.HiddenInput)
    new_password = forms.CharField(required=False, min_length=6, label='Password',widget=forms.PasswordInput(render_value=False))
    confirm_new_password = forms.CharField(required=False, min_length=6, label='Confirm Password',widget=forms.PasswordInput(render_value=False))
    
    def __init__(self,*args,**kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        if(kwargs.has_key('initial')):
            if 'id' not in kwargs['initial']:
                self.fields['new_password'].required = True
                self.fields['confirm_new_password'].required = True
        else:
            if self.data['id'] == '':
                self.fields['new_password'].required = True
                self.fields['confirm_new_password'].required = True
    
    def clean(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        username = cleaned_data.get('username')
        original_username = cleaned_data.get('original_username')
        email = cleaned_data.get('email')
        original_email = cleaned_data.get('original_email')
        id = cleaned_data.get('id')
        
        if id:
            if new_password or confirm_new_password:
                if new_password != confirm_new_password:
                    raise forms.ValidationError("Passwords do not match.")
                
            if original_username != username:
                 #check if username unique
                if User.objects.filter(username=username).count(): 
                    raise forms.ValidationError("A user with this username already exists, please choose another.")
          
            if original_email != email:      
                if User.objects.filter(email=email).count(): 
                    raise forms.ValidationError("A user with this email address already exists, please choose another.")
            
        else:
            #if not new_password or not confirm_new_password:
                #raise forms.ValidationError("Password field is required.")
            #else:
            if new_password != confirm_new_password:
                raise forms.ValidationError("Passwords do not match.")
            
            #check if username unique
            if User.objects.filter(username=username).count(): 
                raise forms.ValidationError("A user with this username already exists, please choose another.")
            if email:
                if User.objects.filter(email=email).count(): 
                    raise forms.ValidationError("A user with this email address already exists, please choose another.")
                
        return cleaned_data

class StudentAccountForm(AccountForm):
    identifier = forms.CharField(max_length=256, label='Student ID', required=True)
    gradelevel = forms.ModelChoiceField(queryset=GradeLevel.objects.filter(deleted=0).order_by('sort_order'), 
                                   label='Grade Level')
    birth_date = forms.DateField(required=True, label='Birth Date')
    organization = forms.ChoiceField(label='Assigned School',
                                             required=True)

    def __init__(self,*args,**kwargs):
        super(StudentAccountForm, self).__init__(*args, **kwargs)
        parent_organization_id = ''
        if(kwargs.has_key('initial')):
            parent_organization_id = kwargs['initial']['parent_organization_id']
        else:
            parent_organization_id = self.data['parent_organization_id']

        schoolList = []    
        for org in Organization.get_schools(parent_organization_id):
            schoolList.append((org.id,org.__unicode__()))
        
        if not len(schoolList):
            org = Organization.objects.get(pk=parent_organization_id)
            schoolList.append((parent_organization_id,org.__unicode__()))
            
        self.fields['organization'].choices =  schoolList