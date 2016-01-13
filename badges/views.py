from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from users.models import *
from organizations.models import *
from badges.models import *
from badges.forms import *
from django.template import loader, Context

@login_required
def list_pathways(request):
    pathway_list = Pathway.get_pathway_list()
 
    return render(request,"admin/managePathways.html", 
                              {'pathway_list':(pathway_list)}) 
    
@login_required
def sort_pathways(request):
    pathway_list = Pathway.get_pathway_list()
 
    return render(request,"admin/sortPathways.html", 
                              {'pathway_list':(pathway_list)}) 

@login_required
def update_pathway_sort(request):
    pathwayList = request.POST.getlist('pathway[]')

    pathwaySortOrders = {}
        
    sort_order = 1
    for v in pathwayList:
        pathway_id = v.replace("pathway_","")
        p = Pathway.objects.get(pk=pathway_id)
        p.sort_order = sort_order
        p.save()
        sort_order+=1
    
    from django.utils import simplejson    
    return HttpResponse(simplejson.dumps([]),mimetype='application/json')

@login_required
def add_pathway(request):
    if request.method == 'POST': 
        form = PathwayForm(request.POST)
            
        if form.is_valid(): 
            badge_image = None
            if 'badge_image' in request.FILES:
                badge_image = request.FILES['badge_image']
                
            Pathway.create_pathway(form.cleaned_data['name'],
                                 form.cleaned_data['pathwaycategory'],
                                 form.cleaned_data['description'],
                                 form.cleaned_data['organization'],
                                 form.cleaned_data['badge_name'],
                                 form.cleaned_data['badge_description'],
                                 form.cleaned_data['badge_criteria'],
                                 badge_image,
                                 form.cleaned_data['badge_points'],
                                 request.user.id)
            
            
            return HttpResponseRedirect('/pathways/')
    else:
        form = PathwayForm(initial={'district_id':request.session['USER_ORGANIZATION_ID']}) 

    return render(request,'admin/addEditPathway.html', {
        'form': form,
    }) 
    
@login_required
def edit_pathway(request, pathway_id):
    p = Pathway.objects.get(pk=pathway_id)
    b = p.get_pathway_badge()
    
    if request.method == 'POST': 
        form = PathwayForm(request.POST)
            
        if form.is_valid(): 
            badge_image = None
            if 'badge_image' in request.FILES:
                badge_image = request.FILES['badge_image']
                
            p.update_pathway(form.cleaned_data['name'],
                                 form.cleaned_data['pathwaycategory'],
                                 form.cleaned_data['description'],
                                 form.cleaned_data['organization'],
                                 form.cleaned_data['badge_name'],
                                 form.cleaned_data['badge_description'],
                                 form.cleaned_data['badge_criteria'],
                                 badge_image,
                                 form.cleaned_data['badge_points'])
            
            
            
            return HttpResponseRedirect('/pathways/')
    else:
        
        form = PathwayForm(initial={'name':p.name,
                                    'pathwaycategory':p.pathwaycategory,
                                   'description':p.description,
                                   'badge_name':b.name,
                                   'badge_description':b.description,
                                   'badge_criteria':b.criteria,
                                   'badge_points':b.points,
                                   'organization':p.get_organization_list(),
                                   'district_id':request.session['USER_ORGANIZATION_ID'],
                                   'id':p.id}) 

    return render(request,'admin/addEditPathway.html', {
        'form': form,
    }) 
    
@login_required
def delete_pathway(request, pathway_id):    
    Pathway.delete_pathway(pathway_id)
    return HttpResponseRedirect('/pathways/')

@login_required
def copy_pathway(request, pathway_id):    
    Pathway.copy_pathway(pathway_id)
    return HttpResponseRedirect('/pathways/')

@login_required
def list_pathway_badges(request):
    pathway_filter = _setup_pathway_filter(request)
    
    badge_list = []
    
    if pathway_filter['selected_pathway_id']:
        for pb in Pathway.get_related_badges(pathway_filter['selected_pathway_id']):
            badge_list.append({'id':pb.badge_id,
                               'image_url':pb.badge.image_url(),
                               'name':pb.badge.name,
                               'sort_order':pb.sort_order})
    
    all_badge_list = []
    for badge in Badge.get_badges():
        all_badge_list.append({'id':badge.id,
                           'identifier':badge.identifier,
                           'name':badge.name,
                           'image_url':badge.image_url(),
                           'grades':badge.assigned_grades()})
    
    return render(request,"admin/managePathwayBadges.html", 
                              {'pathway_list':pathway_filter['pathway_list'],
                               'selected_pathway_id':pathway_filter['selected_pathway_id'],
                               'badge_list':(badge_list),
                               'all_badge_list':all_badge_list})  
    
@login_required
def add_pathway_badge(request, badge_id):
    selected_pathway_id = _get_filter_value('pathway_id', request)
    if selected_pathway_id:
        Pathway.add_badge(selected_pathway_id, badge_id)
        
    return HttpResponseRedirect('/pathways/badges/')

@login_required
def delete_pathway_badge(request, badge_id):
    selected_pathway_id = _get_filter_value('pathway_id', request)
    if selected_pathway_id:
        Pathway.delete_badge(selected_pathway_id, badge_id)
        
    return HttpResponseRedirect('/pathways/badges/')

@login_required
def update_pathway_badges_sort(request):
    badgeList = request.POST.getlist('badge[]')
    selected_pathway_id = _get_filter_value('pathway_id', request)
    
    badgeSortOrders = {}
        
    sort_order = 1
    for v in badgeList:
        badge_id = v.replace("badge_","")
        Pathway.update_badge_sortorder(selected_pathway_id, badge_id, sort_order)
        
        sort_order+=1
    
    from django.utils import simplejson    
    return HttpResponse(simplejson.dumps([]),mimetype='application/json')

@login_required
def list_badges(request, dataOnly=False):
    
    user_role = request.session['USER_ROLE']
    
    badge_list = []
    if user_role == Role.DISTRICTADMIN:
        badge_results = Badge.get_badges(include_inactive=True)
    else:
        badge_results = Badge.get_badges_by_user(request.user.id, include_inactive=True)
        
    for badge in badge_results:
        badge_list.append({'id':badge.id,
                           'identifier':badge.identifier,
                           'name':badge.name,
                           'image_url':badge.image_url(),
                           'grades':badge.assigned_grades()})
    if dataOnly:
        return {'badge_list':(badge_list)}
    else:    
        return render(request,"admin/manageBadges.html", 
                              {'badge_list':(badge_list)}) 
    
    
@login_required
def download_badges(request):
    
    badge_list = []
    if request.session['USER_ROLE'] == Role.DISTRICTADMIN:
        badge_results = Badge.get_badges(include_inactive=True)
    else:
        badge_results = Badge.get_badges_by_user(request.user.id, include_inactive=True)
        
    for badge in badge_results:
        badge_list.append({'id':badge.id,
                           'identifier':badge.identifier,
                           'name':badge.name,
                           'description':badge.description,
                      
                           'lowest_grade':badge.get_lowest_grade(),
                           'highest_grade':badge.get_highest_grade(),
                           'date_created':badge.date_created.strftime('%Y-%m-%d')})
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Badges.csv'
    t = loader.get_template('admin/downloadBadgesTemplate.csv')
    c = Context({'badge_list':(badge_list)})
    response.write(t.render(c))
    return response

    
@login_required
def add_badge(request):
    if request.method == 'POST': 
        form = BadgeForm(request.POST)
       
        if form.is_valid(): 
   
            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
            
            if not form.cleaned_data['points']:
                form.cleaned_data['points'] = 0
           
            Badge.create_badge(form.cleaned_data['identifier'],
                               form.cleaned_data['name'],
                               form.cleaned_data['description'],
                               form.cleaned_data['criteria'],
                               image,
                               form.cleaned_data['is_active'],
                               form.cleaned_data['years_valid'],
                               form.cleaned_data['weight'],
                               form.cleaned_data['points'],
                               form.cleaned_data['allow_send_obi'],
                               form.cleaned_data['gradelevels'],
                               request.user.id)
            
            return HttpResponseRedirect('/badges/')
    else:
        form = BadgeForm(initial={}) 

    return render(request,'admin/addEditBadge.html', {
        'form': form,
    }) 

@login_required
def edit_badge(request, badge_id):
    b = Badge.objects.get(pk=badge_id)
    if request.method == 'POST': 
        form = BadgeForm(request.POST)
            
        if form.is_valid(): 
            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
            
            b.update_badge(form.cleaned_data['identifier'],
                               form.cleaned_data['name'],
                               form.cleaned_data['description'],
                               form.cleaned_data['criteria'],
                               image,
                               form.cleaned_data['is_active'],
                               form.cleaned_data['years_valid'],
                               form.cleaned_data['weight'],
                               form.cleaned_data['points'],
                               form.cleaned_data['allow_send_obi'],
                               form.cleaned_data['gradelevels'] )
            b.save()
            
            return HttpResponseRedirect('/badges/')
    else:
        
        form = BadgeForm(initial={'name':b.name,
                                  'identifier':b.identifier,
                                  'description':b.description,
                                  'criteria':b.criteria,
                                  'is_active':b.is_active,
                                  'years_valid':b.years_valid,
                                  'weight':b.weight,
                                  'points':b.points,
                                  'allow_send_obi':b.allow_send_obi,
                                  'gradelevels':b.get_gradelevel_list(),
                                   'id':b.id}) 

    return render(request,'admin/addEditBadge.html', {
        'form': form,
    }) 

@login_required
def delete_badge(request, badge_id):
    Badge.delete_badge(badge_id)
    return HttpResponseRedirect('/badges/')   

@login_required
def copy_badge(request, badge_id):
    Badge.copy_badge(badge_id)
    return HttpResponseRedirect('/badges/') 

def public_badge_details(request, badge_id):
    b = Badge.objects.get(pk=badge_id)
    badge_details = {'name':b.name,
                      'identifier':b.identifier,
                      'description':b.description,
                      'criteria':b.criteria,
                      'is_active':b.is_active,
                      'years_valid':b.years_valid,
                      'image_url':b.image_url(),
                      'weight':b.weight,
                      'points':b.points,
                      'allow_send_obi':b.allow_send_obi,
                      'gradelevels':b.get_gradelevel_list(),
                       'id':b.id}
    
    return render(request,"publicBadgeDetails.html", 
                              {'badge_details':badge_details}) 
    



@login_required
def list_awards(request):
    school_filter = _setup_school_filter(request)
    student_filter = _setup_student_filter(request)
    award_list = []
    
    if student_filter['selected_student_id']:
        sp = StudentProfile.objects.get(pk=student_filter['selected_student_id'])
        for award in Award.get_user_awards(sp.user_id):
            award_list.append({'id':award.id,
                               'badge_id':award.badge.id,
                               'image_url':award.badge.image_url(),
                               'name':award.badge.name,
                               'date_created':award.date_created.strftime('%m/%d/%Y')})
    all_badge_list = []
    for badge in Badge.get_badges():
        all_badge_list.append({'id':badge.id,
                           'identifier':badge.identifier,
                           'name':badge.name,
                           'image_url':badge.image_url(),
                           'grades':badge.assigned_grades()})
        
    return render(request,"admin/manageAwards.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'student_list':student_filter['student_list'],
                               'selected_student_id':student_filter['selected_student_id'],
                               'all_badge_list':all_badge_list,
                               'award_list':(award_list)}) 
    
@login_required
def issue_award(request):
    student_id = _get_filter_value('student_id', request)
    badge_id = _get_filter_value('badge_id', request)
    
    sp = StudentProfile.objects.get(pk=student_id)
    Award.create_award(sp.user_id,
                       badge_id)
    
    return HttpResponseRedirect('/students/awards/')
   

@login_required
def delete_award(request, award_id):
    Award.delete_award(award_id)
    return HttpResponseRedirect('/students/awards/') 

@login_required
def pathway_summary(request):
    #Get available schools
    school_filter = _setup_school_filter(request, with_all_types=True)
    
    data_set = {}
    if school_filter['selected_school_id']:
        pu_results = None
        if not len(school_filter['selected_school_id']) < 32:
            pu_results = Pathway_User.objects.only('pathway__id','pathway__name').filter(user__organization__id=school_filter['selected_school_id'], 
                                              user__organization__deleted=0,
                                              user__groups__id=1,
                                              user__is_active=1,
                                              pathway__deleted=0,
                                              deleted=0)
        else:
            if school_filter['selected_school_id'] == 'All':
                pu_results = Pathway_User.objects.only('pathway__id','pathway__name').filter( user__organization__deleted=0,
                                             user__groups__id=1,
                                             user__is_active=1,
                                             pathway__deleted=0,
                                             deleted=0)
            else:
                pu_results = Pathway_User.objects.only('pathway__id','pathway__name').filter( user__organization__type_label=school_filter['selected_school_id'], 
                                             user__organization__deleted=0,
                                             user__groups__id=1,
                                             user__is_active=1,
                                             pathway__deleted=0,
                                             deleted=0)
                
        for pu in pu_results:
            if pu.pathway_id not in data_set:
                data_set[pu.pathway_id] = {'id':pu.pathway_id,
                                           'name':pu.pathway.name,
                                           'students':0}
                
            data_set[pu.pathway_id]['students']+=1
            
    return render(request,"reports/pathwaySummary.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'data_set':data_set}) 
    
@login_required
def pathway_badge_completion(request):
    #Get available schools
    school_filter = _setup_school_filter(request, with_all_types=True)
    #pathway_filter = _setup_school_pathway_filter(request, school_filter['selected_school_id'])
    pathway_list = []
    selected_pathway_id = _get_filter_value('pathway_id', request)
    
    student_id_list = []
    
    org_students = []    
    if not len(school_filter['selected_school_id']) < 32: #ugly hack for now
       org_students = Organization.get_students(school_filter['selected_school_id'])
    else:
       org_students = Organization.get_students_by_orgtype(school_filter['selected_school_id'])
    
        
    for user in org_students:
        student_id_list.append(user.user_id)
    
    
    pathwayMap = {}    
    
    for pu in Pathway_User.objects.only('pathway__id','pathway__name').filter(user__in=student_id_list,
                                          pathway__deleted=0,
                                          deleted=0):
        if pu.pathway_id not in pathwayMap:
            pathwayMap[pu.pathway.id] = True
            pathway_list.append({'id':pu.pathway.id,'name':pu.pathway.__unicode__()})
    
    #Default to first pathway in list    
    if selected_pathway_id == 0:
        if(len(pathway_list)):
            selected_pathway_id = pathway_list[0]['id']
            request.session['SELECTED_pathway_id'] = selected_pathway_id
        else:
            pathway_list.append({'id':0,'name':'No pathways found.'})  

    student_list = [] 
    badge_list = []
    
    if selected_pathway_id:
        for pb in Pathway.get_related_badges(selected_pathway_id):
            badge_list.append({'id':pb.badge_id,
                               'name':pb.badge.name})
        
        default_awards = {}
        for badge in badge_list:
            default_awards[badge['id']] = " "    
        
        award_map = {}
        for award in Award.objects.only('id','date_created','user__id','badge__id').filter(deleted=0,user__in=student_id_list):
            if award.user_id not in award_map:
                award_map[award.user_id] = default_awards.copy()
            award_map[award.user_id][award.badge_id] = award.date_created.strftime('%m/%d/%Y')
        
        for user in org_students:
            student_profile = user
            user = user.user
            awards = default_awards
            if user.id in award_map:
                awards = award_map[user.id]
         
            if len(awards):
                student_list.append({'id':student_profile.id,
                                     'name':user.get_full_name(),
                                     'identifier':student_profile.identifier,
                                     'gradelevel':student_profile.gradelevel.short_name(),
                                     'award_map':awards})
    
    return render(request,"reports/pathwayBadgeCompletion.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'pathway_list':pathway_list,
                               'selected_pathway_id':selected_pathway_id,
                               'badge_list':badge_list,
                               'student_list':student_list}) 
    
@login_required
def badge_completion(request):
    #Get available schools
    school_filter = _setup_school_filter(request, with_all_types=True)

    student_list = [] 
    student_id_list = []
    badge_list = []
    
    if school_filter['selected_school_id']:
        for b in Badge.get_badges():
            badge_list.append({'id':b.id,
                               'name':b.name})
            
        default_awards = {}
        for badge in badge_list:
            default_awards[badge['id']] = " "
     
        org_students = []
        if not len(school_filter['selected_school_id']) < 32: #ugly hack for now
           org_students = Organization.get_students(school_filter['selected_school_id'])
        else:
           org_students = Organization.get_students_by_orgtype(school_filter['selected_school_id'])
           
        for user in org_students:
            student_id_list.append(user.user_id)

        award_map = {}
        for award in Award.objects.only('id','date_created','user__id','badge__id').filter(deleted=0,user__in=student_id_list):
            if award.user_id not in award_map:
                award_map[award.user_id] = default_awards.copy()
       
            award_map[award.user_id][award.badge_id] = award.date_created.strftime('%m/%d/%Y')
        
        for user in org_students:
            student_profile = user
            user = user.user
            awards = default_awards
            if user.id in award_map:
                awards = award_map[user.id]

            gradelevel_name = ''
            if student_profile.gradelevel:
            	gradelevel_name = student_profile.gradelevel.short_name()
      
            student_list.append({'id':student_profile.id,
                                 'name':user.get_full_name(),
                                 'identifier':student_profile.identifier,
                                 'gradelevel':gradelevel_name,
                                 'email':user.email,
                                 'award_map':awards})

    return render(request,"reports/badgeCompletion.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'badge_list':badge_list,
                               'student_list':student_list}) 
   

def _setup_student_filter(request):
    student_list = []
    selected_student_id = _get_filter_value('student_id', request)
    selected_school_id = _get_filter_value('school_id', request)
    
    if selected_school_id:
        for user in Organization.get_students(selected_school_id):
            student_list.append({'id':user.id,
                                 'name':user.user.get_full_name()})
                                 
    #Default to first pathway in list    
    if selected_student_id == 0:
        if(len(student_list)):
            selected_student_id = student_list[0]['id']
            request.session['SELECTED_student_id'] = selected_student_id
        else:
            student_list.append({'id':0,'name':'No students created.'})  
            
    return {'student_list':student_list,
            'selected_student_id':selected_student_id}


def _setup_pathway_filter(request):
    pathway_list = []
    selected_pathway_id = _get_filter_value('pathway_id', request)
    
    results = Pathway.get_pathways()
                                    
    for obj in results:
        pathway_list.append({'id':obj.id,'name':obj.__unicode__()})
   
    #Default to first pathway in list    
    if selected_pathway_id == 0:
        if(len(pathway_list)):
            selected_pathway_id = pathway_list[0]['id']
            request.session['SELECTED_pathway_id'] = selected_pathway_id
        else:
            pathway_list.append({'id':0,'name':'No pathways created.'})  
            
    return {'pathway_list':pathway_list,
            'selected_pathway_id':selected_pathway_id}
   
    
def _setup_school_filter(request, with_all_types=False):
    school_list = []
    type_list = {}
    selected_school_id = _get_filter_value('school_id', request)
    
    if(request.session['USER_ORGANIZATION_TYPE'] == Organization.TYPE_SCHOOL):
        school_list.append({'id':request.session['USER_ORGANIZATION_ID'],
                           'name':request.session['USER_ORGANIZATION_NAME']})
    else:
        results = Organization.get_schools(request.session['USER_ORGANIZATION_ID'])
                                    
        for obj in results:
            if obj.type_label and obj.type_label not in type_list: 
                type_list[obj.type_label] = True
            school_list.append({'id':obj.id,'name':obj.__unicode__()})
   
    #Default to first school in list    
    if selected_school_id == 0 or (selected_school_id == -1 and not with_all_types):
        if(len(school_list)):
            selected_school_id = school_list[0]['id']
            request.session['SELECTED_school_id'] = selected_school_id
        else:
            school_list.append({'id':0,'name':'No schools created.'})  
            
    if with_all_types:
        for key,value in type_list.items():
            school_list.insert(0,{'id':key,'name':'All '+key+' Schools'})
        #school_list.insert(0,{'id':'All','name':'All Schools'})
            
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



###STUDENT VIEWS

def obi_assertion(request, award_id):
    award = Award.objects.get(pk=award_id)
    
    url = None
    if award.badge.image:
        url = award.badge.image.url

    expiration_date = ''
    if award.expiration_date:
        expiration_date = award.expiration_date.strftime('%Y-%m-%d')
    
    description = award.badge.description
    
    import hashlib
    from django.utils import simplejson
    
    emailAddress = award.user.email

    secretKey = "passport2success"
    recipient = m = hashlib.sha256()
    m.update(emailAddress + secretKey)

    issuer_name = 'Passport To Success'
    issuer_org = 'Corona-Norco Unified School District'
    issuer_contact = 'info@cnusd-p2s.org'
    
    if award.badge.system.issuer_name:
        issuer_name = award.badge.system.issuer_name
    if award.badge.system.issuer_contact:
        issuer_contact = award.badge.system.issuer_contact
    if award.badge.system.issuer_org:
        issuer_org = award.badge.system.issuer_org

    assertion = {'recipient':'sha256$'+m.hexdigest(),
             'salt':secretKey,
             'evidence':'',
             'expires':expiration_date,
             'issued_on':award.date_created.strftime('%Y-%m-%d'),
             'badge': {'version':"0.5.0",
                       'name':award.badge.name,
                       'image':url,
                       'description':description[0:127],
                       'criteria':'http://'+request.get_host()+'/badges/criteria/'+award.badge_id+'/',
                       'issuer':{'origin':'http://'+request.get_host(),
                                'name':issuer_name,
                                'org':issuer_org,
                                'contact':issuer_contact}}}
    
    return HttpResponse(simplejson.dumps(assertion),mimetype='application/json')
    
@login_required
def my_badges(request):
    award_list = []
    for award in Award.get_user_awards(request.user.id):
        award_list.append({'id':award.id,
                           'badge_id':award.badge.id,
                           'image_url':award.badge.image_url(),
                           'name':award.badge.name,
                           'date_created':award.date_created.strftime("%m/%d/%Y"),
                           'pathway_names':award.badge.get_mapped_pathway_names(),
                           'points':award.points})
        
    return render(request,"my_badges.html", 
                              {'award_list':award_list,}) 
    
@login_required
def my_pathways(request):
    pathway_list = Pathway.get_user_pathway_list(request.user.id)
    
    exclude_list = []
    for pathway in pathway_list:
        exclude_list.append(pathway['id'])
    
    all_pathway_list = Pathway.get_pathway_list(organization_id=request.session['USER_ORGANIZATION_ID'],
                                                exclude_list=exclude_list)
    
    
    return render(request,"my_pathways.html", 
                              {'pathway_list':pathway_list,
                               'all_pathway_list':all_pathway_list})
    
@login_required
def update_my_pathways_sort(request):
    pathwayList = request.POST.getlist('pathway[]')

    pathwaySortOrders = {}
        
    sort_order = 1
    for v in pathwayList:
        pathway_id = v.replace("pathway_","")
        for p in Pathway_User.objects.filter(pathway=pathway_id,user=request.user,deleted=0):
            p.sort_order = sort_order
            p.save()
            sort_order+=1
    
    from django.utils import simplejson    
    return HttpResponse(simplejson.dumps([]),mimetype='application/json')
    
@login_required
def add_my_pathway(request, pathway_id):
     Pathway.add_user_pathway(request.user.id, pathway_id)
     return HttpResponseRedirect('/my_pathways/')
 
@login_required
def delete_my_pathway(request, pathway_id):
     Pathway.delete_user_pathway(request.user.id, pathway_id)
     return HttpResponseRedirect('/my_pathways/')
 
 
@login_required
def bulk_issue(request):
    if request.method == 'POST': 
        form = BulkIssueForm(request.POST, request.FILES)
        if form.is_valid(): 
            file = None
            if 'file' in request.FILES:
                file = request.FILES['file']
            
            BulkIssueQueue.schedule_bulk_import(file,
                               form.cleaned_data['email'],
                               request.session['USER_ORGANIZATION_ID'],
                               request.user.id)
            
            return HttpResponseRedirect('/badges/bulk_issue_complete/')
    else:
        form = BulkIssueForm(initial={}) 

    return render(request,'admin/bulkIssue.html', {
        'form': form,
    }) 

@login_required
def bulk_issue_complete(request):
    return render(request,'admin/bulkIssueComplete.html', {})

@login_required
def download_sample_bulk_file(request):
    from django.template import loader, Context
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=SampleBadgeIssueImport.csv'
    
    t = loader.get_template('admin/Vendor_Badge_Import.csv')
    c = Context()
    response.write(t.render(c))
    return response    
    
