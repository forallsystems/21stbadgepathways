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

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as django_auth_views
from common.forms import *
from datetime import datetime

def custom_logout(request):
    
    redirect_to = "/"
    
    if 'ORG_SETTINGS' in request.session and request.session['ORG_SETTINGS']:
        redirect_to = "/"+request.session['ORG_SETTINGS'].login_url+"/"
        
    django_auth_views.logout(request)
    
    print redirect_to
         
    return HttpResponseRedirect(redirect_to)      
    

def custom_login(request, url="", template_name='login.html',
                 redirect_field_name=REDIRECT_FIELD_NAME,
                 authentication_form=CustomAuthenticationForm):
    
    is_preview = request.REQUEST.get('preview', 0)

    
    if request.user.is_authenticated() and not is_preview:
       return HttpResponseRedirect("/dashboard/")
   
    #verify url    
    settings = None
    if url:
        for os in  Organization_Settings.objects.filter(deleted=0, login_url=url):
            settings = os
    
    
    if  settings:
        request.session['ORG_SETTINGS'] = settings
        request.session['USER_ORGANIZATION_NAME'] = settings.organization.name
    
    
    
    """Displays the login form and handles the login action."""
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            django_auth_views.auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                
            log = LogInHistory(user=form.get_user(), date=datetime.now(), ip=request.META['REMOTE_ADDR'])
            log.save()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
    }, context_instance=RequestContext(request))

@login_required
def list_schools(request):
    school_list = []
    
    results = Organization.get_schools(request.session['USER_ORGANIZATION_ID'])
                                    
    for obj in results:
        school_list.append({'id':obj.id,
                            'name':obj.__unicode__(),
                            'enable_store':obj.enable_store,
                            'enable_custom_login':obj.enable_custom_login,
                            'organization_id':obj.organization_id,
                            'total_accounts':len(Organization.get_schooladmins(obj.id))})
                              
    return render(request,"admin/manageSchools.html", 
                              {'school_list':(school_list)}) 
    
@login_required
def add_school(request):
    if request.method == 'POST': 
        form = SchoolForm(request.POST)
            
        if form.is_valid(): 
            
            
            Organization.create_organization(request.session['USER_ORGANIZATION_ID'], 
                                             form.cleaned_data['name'], 
                                             Organization.TYPE_SCHOOL, 
                                             '',
                                             form.cleaned_data['enable_store'],
                                             form.cleaned_data['enable_custom_login'],
                                             form.cleaned_data['organization_id'])
            
            return HttpResponseRedirect('/schools/')
    else:
        form = SchoolForm() 

    return render(request,'admin/addEditSchool.html', {
        'form': form,
    }) 
    
@login_required
def edit_school(request, school_id):
    
    org = Organization.objects.get(pk=school_id)
    settings = org.init_settings()
    
    if request.method == 'POST': 
        form = SchoolForm(request.POST)
            
        if form.is_valid(): 
           
            org.update_organization(form.cleaned_data['name'],
                                    form.cleaned_data['organization_id'],
                                    form.cleaned_data['enable_store'],
                                    form.cleaned_data['enable_custom_login'])
            org.save()
            
            settings.login_url = form.cleaned_data['login_url']
            settings.save()
            
            return HttpResponseRedirect('/schools/')
    else:
        
        
        
        form = SchoolForm(initial={'name':org.name,
                                  'enable_store':org.enable_store,
                                  'enable_custom_login':org.enable_custom_login,
                                  'organization_id':org.organization_id,
                                  'login_url':settings.login_url,
                                   'id':org.id}) 

    return render(request,'admin/addEditSchool.html', {
        'form': form,
    }) 
    
@login_required
def edit_settings(request):
    if(request.session['USER_ORGANIZATION_TYPE'] == Organization.TYPE_SCHOOL):
        org = Organization.objects.get(pk=request.session['USER_ORGANIZATION_ID'])
        settings = org.init_settings()
        
        if request.method == 'POST': 
            form = SchoolSettingsForm(request.POST)
                
            if form.is_valid(): 
                primary_logo = None
                if 'primary_logo' in request.FILES:
                    primary_logo = request.FILES['primary_logo']
                
                org.update_settings(form.cleaned_data['login_url'],
                                   primary_logo,
                                   form.cleaned_data['login_text'],
                                   form.cleaned_data['login_text_background_color'],
                                   form.cleaned_data['login_text_color'],
                                   form.cleaned_data['header_color'],
                                   form.cleaned_data['background_color'],
                                   form.cleaned_data['text_color'])
                settings = org.init_settings()
                request.session['ORG_SETTINGS'] = settings
             
        else:
            
            form = SchoolSettingsForm(initial={
                                           'id':settings.id,
                                          'login_url':settings.login_url,
                                          'primary_logo':settings.primary_logo,
                                          'login_text':settings.login_text if settings.login_text else "Welcome to CNUSD's Passport to Success eBadge website. Students, enter your username and password below to login and begin your journey through digital badges!",
                                          'login_text_background_color':settings.login_text_background_color,
                                          'login_text_color':settings.login_text_color,
                                          'header_color':settings.header_color,
                                          'background_color':settings.background_color,
                                          'text_color':settings.text_color
                                       }) 
    
        return render(request,'admin/editSchoolSettings.html', {
            'form': form,
            'login_url':settings.login_url,
            'primary_logo_url':settings.primary_logo.url if settings.primary_logo else ''
        }) 
        
    else:
        return HttpResponseRedirect('/dashboard/')
    
    

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