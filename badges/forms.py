from django import forms
from django.contrib.auth.models import User
from bootstrap.forms import BootstrapForm, Fieldset
from organizations.models import *
from badges.models import *
import os
class PathwayForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    district_id = forms.CharField(required=True, widget=forms.HiddenInput)
    name = forms.CharField(max_length=256, label='Pathway Name')
    pathwaycategory = forms.ModelChoiceField(queryset=PathwayCategory.objects.filter(deleted=0).order_by('name'), 
                                   label='Pathway Category')
    description = forms.CharField(label='Pathway Description', widget=forms.Textarea,required=False)
    organization = forms.MultipleChoiceField(label='Assigned School(s)',
                                             required=False,
                                             help_text='<span style="font-size:.9em;">Hold Ctrl/Cmd to select multiple schools.</i></span>')

    badge_name = forms.CharField(max_length=256, label='Pathway Badge Name')
    badge_description = forms.CharField(label='Pathway Badge Description', widget=forms.Textarea,required=False)
    badge_criteria = forms.CharField(label='Pathway Badge Criteria', widget=forms.Textarea,required=False)
    badge_image  = forms.ImageField(label='Pathway Badge Image', required=False)
    badge_points = forms.IntegerField(label='Pathway Badge Point Value', min_value=0)

    def __init__(self,*args,**kwargs):
        super(PathwayForm, self).__init__(*args, **kwargs)
        district_id = ''
        if(kwargs.has_key('initial')):
            district_id = kwargs['initial']['district_id']
        else:
            district_id = self.data['district_id']

        schoolList = []    
        for org in Organization.get_schools(district_id):
            schoolList.append((org.id,org.__unicode__()))
            
        self.fields['organization'].choices =  schoolList
        
class BadgeClaimForm(BootstrapForm):
    code = forms.CharField(max_length=256, label='Claim Code')
    
    def clean(self):
        
        cleaned_data = super(BootstrapForm, self).clean()
        code =  cleaned_data.get('code')

        if Claim.objects.filter(code=code).count() == 0:
            raise forms.ValidationError("Invalid claim code entered.")
        
        code = Claim.objects.get(code=code)
        if(code.last_claimed_date):
            raise forms.ValidationError("This claim code has already been claimed.")
        
        
               
        return cleaned_data
        
class BadgeForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    identifier = forms.CharField(max_length=256, label='Badge ID')
    name = forms.CharField(max_length=256, label='Badge Name')
    description = forms.CharField(label='Badge Description', widget=forms.Textarea,required=False)
    criteria = forms.CharField(label='Badge Criteria', widget=forms.Textarea,required=False)
    
    image  = forms.ImageField(label='Badge Image', required=False)
    
    is_active = forms.BooleanField(label='Active', required=False)
    years_valid = forms.IntegerField(label='Years to Archive', min_value=0)
    weight = forms.IntegerField(label='Badge Weighting', min_value=0)
    points = forms.IntegerField(label='Point Value', min_value=0, required=False)
    allow_send_obi = forms.BooleanField(label='Allow Sending to the Mozilla Badge Backpack', required=False)
    allow_issue_mutiple = forms.BooleanField(label='Allow Badge to be Earned Multiple Times', required=False)
    
    gradelevels = forms.ModelMultipleChoiceField(queryset=GradeLevel.objects.filter(deleted=0).order_by('sort_order'), 
                                   label='Assigned Grade Level(s)',
                                   help_text='<span style="font-size:.9em;">Hold Ctrl/Cmd to select multiple grades.</i></span>')

class AwardForm(BootstrapForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    badge = forms.ModelChoiceField(queryset=Badge.objects.filter(deleted=0).order_by('name'), 
                                   label='Badge')
    
class BulkIssueForm(BootstrapForm):
    file  = forms.FileField(label='Upload CSV File', required=True)
    email = forms.CharField(max_length=256, label='Notification Email Address')
    
    def clean(self):
        
        cleaned_data = super(BootstrapForm, self).clean()
        file =  cleaned_data.get('file')

        filename = file.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()

        if ext != '.csv':
            raise forms.ValidationError("Only CSV files are supported.")
        return cleaned_data
    