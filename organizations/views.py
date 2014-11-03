from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
##from django.views.generic.simple import direct_to_template
from django.shortcuts import render
from django.db.models import Count
from users.models import *
from organizations.models import *
from organizations.forms import *
from social.apps.django_app.default.models import *


@login_required
def list_schools(request):
    school_list = []
    
    results = Organization.get_schools(request.session['USER_ORGANIZATION_ID'])
                                    
    for obj in results:
        school_list.append({'id':obj.id,
                            'name':obj.__unicode__(),
                            'enable_store':obj.enable_store,
                            'organization_id':obj.organization_id,
                            'total_accounts':len(Organization.get_schooladmins(obj.id))})
                              
    return render(request,"admin/manageSchools.html", 
                              {'school_list':(school_list)}) 
    
@login_required
def edit_school(request, school_id):
    
    org = Organization.objects.get(pk=school_id)
    if request.method == 'POST': 
        form = SchoolForm(request.POST)
            
        if form.is_valid(): 
           
            org.update_organization(form.cleaned_data['name'],
                                    form.cleaned_data['organization_id'],
                                    form.cleaned_data['enable_store'])
            org.save()
            
            return HttpResponseRedirect('/schools/')
    else:
        
        form = SchoolForm(initial={'name':org.name,
                                  'enable_store':org.enable_store,
                                  'organization_id':org.organization_id,
                                   'id':org.id}) 

    return render(request,'admin/addEditSchool.html', {
        'form': form,
    }) 
    

def _setup_school_filter(request):
    school_list = []
    selected_school_id = _get_filter_value('school_id', request)
    
    if(request.session['USER_ORGANIZATION_TYPE'] == Organization.TYPE_SCHOOL):
        school_list.append({'id':request.session['USER_ORGANIZATION_ID'],
                           'name':request.session['USER_ORGANIZATION_NAME']})
    else:
        results = Organization.get_schools(request.session['USER_ORGANIZATION_ID'])
                                    
        for obj in results:
            school_list.append({'id':obj.id,'name':obj.__unicode__()})
   
    #Default to first school in list    
    if selected_school_id == 0:
        if(len(school_list)):
            selected_school_id = school_list[0]['id']
            request.session['SELECTED_school_id'] = selected_school_id
        else:
            school_list.append({'id':0,'name':'No schools created.'})  
            
    return {'school_list':school_list,
            'selected_school_id':selected_school_id}
    

    
def _get_filter_value(name, request):
    selected_value = request.REQUEST.get(name,0)
    
    if selected_value: #store selected value in session, so we don't have to pass it around in the GET params
        request.session['SELECTED_'+name] = selected_value
    else:
        if 'SELECTED_'+name in request.session:
            selected_value = request.session['SELECTED_'+name]

    if selected_value == '0':
        selected_value = 0        
    return selected_value