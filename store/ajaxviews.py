from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from users.models import *
from organizations.models import *
from store.models import *
from badges.models import *
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_item_details(request):
    item_id = request.POST['item_id']
    b = Item.objects.get(pk=item_id)
    
    data = {'id':b.id,
            'name':b.name,
            'description':b.description,
            'image_url':b.image_url()}
    
    return HttpResponse(simplejson.dumps({'data':data}),mimetype='application/json')
