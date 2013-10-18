from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from users.models import *
from organizations.models import *
from store.models import *
from badges.models import *
from django.utils import simplejson


def get_pathway_badges(request):
  
    pathway_id = request.POST['pathway_id']
    
    badge_list = []
    
   
    for pb in Pathway.get_related_badges(pathway_id):
        badge_list.append({'id':pb.badge_id,
                           'image_url':pb.badge.image_url(),
                           'name':pb.badge.name,
                           'sort_order':pb.sort_order})
        
    return HttpResponse(simplejson.dumps({'data':badge_list}),mimetype='application/json')

def get_pathway_awards(request):
    pathway_id = request.POST['pathway_id']
    
    badge_list = []
    
   
    for pb in Pathway.get_related_badges(pathway_id):
        badge_list.append({'id':pb.badge_id,
                           'image_url':pb.badge.image_url(),
                           'name':pb.badge.name,
                           'allow_send_obi':pb.badge.allow_send_obi,
                           'sort_order':pb.sort_order})
        
    award_list = {}
    for award in Award.get_user_awards_by_pathway(request.user.id, pathway_id):
        award_list[award.badge_id] = {'date_created':award.date_created.strftime('%m/%d/%Y'),
                                      'award_id':award.id}
        
    return HttpResponse(simplejson.dumps({'badge_list':badge_list, 'award_list':award_list}),mimetype='application/json')

def get_pathway_details(request):
    
    pathway_id = request.POST['pathway_id']
    p = Pathway.objects.get(pk=pathway_id)
    
    data = {'id':p.id,
            'name':p.name,
            'description':p.description,
            'image_url':p.get_pathway_badge().image_url()}
   
    return HttpResponse(simplejson.dumps({'data':data}),mimetype='application/json')


def get_badge_details(request):
    badge_id = request.POST['badge_id']
    b = Badge.objects.get(pk=badge_id)
    
    data = {'id':b.id,
            'name':b.name,
            'description':b.description,
            'criteria':b.criteria,
            'image_url':b.image_url()}
    
    return HttpResponse(simplejson.dumps({'data':data}),mimetype='application/json')

def get_award_details(request):
    award_id = request.POST['award_id']
    a = Award.objects.get(pk=award_id)

    data = {'id':a.id,
            'date_created':a.date_created.strftime('%m/%d/%Y'),
            'badge_id':a.badge_id,
            'name':a.badge.name,
            'description':a.badge.description,
            'criteria':a.badge.criteria,
            'image_url':a.badge.image_url()}
    
    return HttpResponse(simplejson.dumps({'data':data}),mimetype='application/json')