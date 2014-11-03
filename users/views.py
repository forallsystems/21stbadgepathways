from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
##from django.views.generic.simple import direct_to_template
from django.shortcuts import render
from django.db.models import Count
from users.models import *
from organizations.models import *
from users.forms import *
from social.apps.django_app.default.models import *

@login_required
def edit_myaccount_info(request):
    user = request.user
    if request.method == 'POST': 
        form = AccountForm(request.POST)
        if form.is_valid(): 
            
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            
            
            if form.cleaned_data['new_password']:
                user.set_password(form.cleaned_data['new_password'])
                
            user.save()
 
            return HttpResponseRedirect('/dashboard/')
    else:
        
        form = AccountForm(initial={'first_name':user.first_name,
                                       'last_name':user.last_name,
                                       'username':user.username,
                                       'original_username':user.username,
                                       'email':user.email,
                                       'original_email':user.email,
                                       'id':user.id
                                       }) 
    
    #see if they are linked to google
    hasGoogleLink = False
    hasPersonaLink = False
    googleUsername = ''
    personaUsername = ''
    
    for sa in UserSocialAuth.objects.filter(user=user, provider='google-oauth2'):
        hasGoogleLink = sa.id
        googleUsername = sa.uid
        
    for sa in UserSocialAuth.objects.filter(user=user, provider='persona'):
        hasPersonaLink = sa.id
        personaUsername = sa.uid
    
    return render(request,'myAccountInfo.html', {
        'form': form,
        'hasGoogleLink':hasGoogleLink,
        'hasPersonaLink':hasPersonaLink,
        'googleUsername':googleUsername,
        'personaUsername':personaUsername
        
    }) 
    
def authError(request):
     return render(request,'socialAuthError.html', {})
    
    
@login_required
def edit_myaccount(request):
    user = request.user
    if request.method == 'POST': 
        form = AccountForm(request.POST)
        if form.is_valid(): 
            
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            
            
            if form.cleaned_data['new_password']:
                user.set_password(form.cleaned_data['new_password'])
                
            user.save()
 
            return HttpResponseRedirect('/dashboard/')
    else:
        
        form = AccountForm(initial={'first_name':user.first_name,
                                       'last_name':user.last_name,
                                       'username':user.username,
                                       'original_username':user.username,
                                       'email':user.email,
                                       'original_email':user.email,
                                       'id':user.id
                                       }) 

    return render(request,'myAccount.html', {
        'form': form,
    }) 
    
    
@login_required
def list_schooladmins(request):
    schooladmin_list = []
    school_filter = _setup_school_filter(request)
    if school_filter['selected_school_id']:
        for user in Organization.get_schooladmins(school_filter['selected_school_id']):
            schooladmin_list.append({'id':user.get_profile().id,
                                     'name':user.get_full_name(),
                                     'email':user.email})
                              
    return render(request,"admin/manageSchoolAdmins.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'schooladmin_list':(schooladmin_list)}) 
    
@login_required
def add_schooladmin(request, school_id):
    if request.method == 'POST': 
        form = AccountForm(request.POST)
            
        if form.is_valid(): 
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'],form.cleaned_data['new_password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            user.groups.add(Role.SCHOOLADMIN)
            
            user_to_org = Organization_User(user=user,
                                            organization_id=school_id)
            user_to_org.save()

            return HttpResponseRedirect('/schooladmins/?schoolid='+school_id)
    else:
        form = AccountForm(initial={}) 

    return render(request,'admin/addEditSchoolAdmin.html', {
        'form': form,
    }) 
    
@login_required
def edit_schooladmin(request, userprofile_id):
    if request.method == 'POST': 
        form = AccountForm(request.POST)
            
        if form.is_valid(): 
            user = User.objects.get(pk=form.cleaned_data['id'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            
            if form.cleaned_data['new_password']:
                user.set_password(form.cleaned_data['new_password'])
            
            return HttpResponseRedirect('/schooladmins/')
    else:
        up = UserProfile.objects.get(pk=userprofile_id)
        form = AccountForm(initial={'first_name':up.user.first_name,
                                           'last_name':up.user.last_name,
                                           'username':up.user.username,
                                           'original_username':up.user.username,
                                           'email':up.user.email,
                                           'original_email':up.user.email,
                                           'id':up.user.id}) 

    return render(request,'admin/addEditSchoolAdmin.html', {
        'form': form,
    }) 
    
@login_required
def delete_schooladmin(request, userprofile_id):
    up = UserProfile.objects.get(pk=userprofile_id)
    up.user.is_active = 0
    up.user.save()
    
    Organization.remove_user(up.user_id)
    
    return HttpResponseRedirect('/schooladmins/')
    

@login_required
def list_districtadmins(request):
    districtadmin_list = []
    
    for user in Organization.get_districtadmins(request.session['USER_ORGANIZATION_ID']):
        districtadmin_list.append({'id':user.get_profile().id,
                                     'name':user.get_full_name(),
                                     'email':user.email})
                              
    return render(request,"admin/manageDistrictAdmins.html", 
                              {'districtadmin_list':(districtadmin_list)}) 
    
@login_required
def add_districtadmin(request):
    if request.method == 'POST': 
        form = AccountForm(request.POST)
            
        if form.is_valid(): 
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'],form.cleaned_data['new_password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            user.groups.add(Role.DISTRICTADMIN)
            
            user_to_org = Organization_User(user=user,
                                            organization_id=request.session['USER_ORGANIZATION_ID'])
            user_to_org.save()

            return HttpResponseRedirect('/districtadmins/')
    else:
        form = AccountForm(initial={}) 

    return render(request,'admin/addEditDistrictAdmin.html', {
        'form': form,
    }) 

@login_required
def edit_districtadmin(request, userprofile_id):
    if request.method == 'POST': 
        form = AccountForm(request.POST)
            
        if form.is_valid(): 
            user = User.objects.get(pk=form.cleaned_data['id'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            
            if form.cleaned_data['new_password']:
                user.set_password(form.cleaned_data['new_password'])
            
            return HttpResponseRedirect('/districtadmins/')
    else:
        up = UserProfile.objects.get(pk=userprofile_id)
        form = AccountForm(initial={'first_name':up.user.first_name,
                                           'last_name':up.user.last_name,
                                           'username':up.user.username,
                                           'original_username':up.user.username,
                                           'email':up.user.email,
                                           'original_email':up.user.email,
                                           'id':up.user.id}) 

    return render(request,'admin/addEditDistrictAdmin.html', {
        'form': form,
    }) 
    
@login_required
def delete_districtadmin(request, userprofile_id):
    up = UserProfile.objects.get(pk=userprofile_id)
    up.user.is_active = 0
    up.user.save()
    
    Organization.remove_user(up.user_id)
    
    return HttpResponseRedirect('/districtadmins/')

@login_required
def list_students(request):
    #Get available schools
    school_filter = _setup_school_filter(request)
    
    student_list = []
    
    userAwardMap = {}
    user_awards = User.objects.annotate(award_num=Count('award__badge',distinct=True)).filter(award__deleted=0, organization_user__organization=school_filter['selected_school_id'])
    for ua in user_awards:
        userAwardMap[ua.id] = ua.award_num
    
    if school_filter['selected_school_id']:
        for student_profile in Organization.get_students(school_filter['selected_school_id']):
            num_awards = 0
            if student_profile.user.id in userAwardMap:
                num_awards = userAwardMap[student_profile.user.id]
            student_list.append({'id':student_profile.id,
                                 'name':student_profile.user.get_full_name(),
                                 'identifier':student_profile.identifier,
                                 'username':student_profile.user.username,
                                 'email':student_profile.user.email,
                                 'num_awards':num_awards})#Award.get_user_num_awards(student_profile.user.id)})
                              
    return render(request,"admin/manageStudents.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'student_list':(student_list)}) 
    
@login_required
def add_student(request, school_id):
    if request.method == 'POST': 
        form = StudentAccountForm(request.POST)
        if form.is_valid(): 
            StudentProfile.create_student(form.cleaned_data['username'],
                                          form.cleaned_data['email'],
                                          form.cleaned_data['new_password'],
                                          form.cleaned_data['first_name'],
                                          form.cleaned_data['last_name'],
                                          form.cleaned_data['organization'],
                                          form.cleaned_data['identifier'],
                                          form.cleaned_data['gradelevel'],
                                          form.cleaned_data['birth_date'])
            
            return HttpResponseRedirect('/students/?school_id='+form.cleaned_data['organization'])
    else:
        form = StudentAccountForm(initial={'parent_organization_id':request.session['USER_ORGANIZATION_ID']}) 

    return render(request,'admin/addEditStudent.html', {
        'form': form,
    }) 
    
@login_required
def edit_student(request, studentprofile_id):
    if request.method == 'POST': 
        form = StudentAccountForm(request.POST)
        if form.is_valid(): 
            user = User.objects.get(pk=form.cleaned_data['id'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            
            
            if form.cleaned_data['new_password']:
                user.set_password(form.cleaned_data['new_password'])
            user.save()
            sp = user.get_profile().get_student_profile();
            sp.identifier = form.cleaned_data['identifier']
            sp.gradelevel = form.cleaned_data['gradelevel']
            sp.birth_date = form.cleaned_data['birth_date']
            sp.save()
            
            if sp.get_school().id != form.cleaned_data['organization']:
                sp.move_student(form.cleaned_data['organization'])
            
            return HttpResponseRedirect('/students/')
    else:
        sp = StudentProfile.objects.get(pk=studentprofile_id)
        birth_date = ''
        if sp.birth_date:
            birth_date = sp.birth_date.strftime('%m/%d/%Y')
  
        form = StudentAccountForm(initial={'first_name':sp.user.first_name,
                                           'last_name':sp.user.last_name,
                                           'username':sp.user.username,
                                           'original_username':sp.user.username,
                                           'email':sp.user.email,
                                           'original_email':sp.user.email,
                                           'identifier':sp.identifier,
                                           'gradelevel':sp.gradelevel,
                                           'birth_date':birth_date,
                                           'id':sp.user.id,
                                           'organization':sp.get_school().id,
                                    
                                           'parent_organization_id':request.session['USER_ORGANIZATION_ID']}) 

    return render(request,'admin/addEditStudent.html', {
        'form': form,
    }) 
    
@login_required
def delete_student(request, studentprofile_id):
    sp = StudentProfile.objects.get(pk=studentprofile_id)
    sp.user.is_active = 0
    sp.user.save()
    
    Organization.remove_student(sp.user_id)
    
    return HttpResponseRedirect('/students/')

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