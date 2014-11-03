from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
##from django.views.generic.simple import direct_to_template
from django.shortcuts import render
from django.db.models import Count
from users.models import *
from organizations.models import *
from store.models import *
from store.forms import *
import badges.views as badges_views

@login_required
def list_vendors(request):
    #Get available schools
    vendor_list = []
    
    for vendor in Vendor.get_vendors():  
        vendor_list.append({'id':vendor.id,
                             'name':vendor.name,
                             'total_items':vendor.total_items(),
                             'image_url':vendor.image_url()})
                              
    return render(request,"admin/manageVendors.html", 
                              {'vendor_list':(vendor_list)}) 

@login_required
def add_vendor(request):
    if request.method == 'POST': 
        form = VendorForm(request.POST)
            
        if form.is_valid(): 
            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
            
            Vendor.create_vendor(form.cleaned_data['name'], image)
            
            
            return HttpResponseRedirect('/vendors/')
    else:
        form = VendorForm(initial={}) 

    return render(request,'admin/addEditVendor.html', {
        'form': form,
    }) 
    
@login_required
def edit_vendor(request, vendor_id):
    if request.method == 'POST': 
        form = VendorForm(request.POST)
            
        if form.is_valid(): 
            v = Vendor.objects.get(pk=form.cleaned_data['id'])
            v.name = form.cleaned_data['name']
            if 'image' in request.FILES:
                v.image = request.FILES['image']
            v.save()
            
            return HttpResponseRedirect('/vendors/')
    else:
        v = Vendor.objects.get(pk=vendor_id)
        form = VendorForm(initial={'name':v.name,
                                   'id':v.id}) 

    return render(request,'admin/addEditVendor.html', {
        'form': form,
    }) 
    
@login_required
def delete_vendor(request, vendor_id):
    Vendor.delete_vendor(vendor_id)
    return HttpResponseRedirect('/vendors/')

@login_required
def list_items(request):
    school_filter = _setup_school_filter(request)
    
    item_list = []
    
    if school_filter['selected_school_id']:
        for item in Item.get_items_in_school(school_filter['selected_school_id']):
            item_list.append({'id':item.id,
                                 'name':item.name,
                                 'description':item.description,
                                 'points':item.points,
                                 'inventory':item.inventory,
                                 'image_url':item.image_url()})
                              
    return render(request,"admin/manageItems.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'item_list':(item_list)})   
    
@login_required
def add_item(request, school_id):
    if request.method == 'POST': 
        form = ItemForm(request.POST)
            
        if form.is_valid(): 
            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
                
            Item.create_item(None,
                             form.cleaned_data['name'],
                             form.cleaned_data['description'],
                             form.cleaned_data['points'],
                             form.cleaned_data['inventory'],
                             image,
                             [school_id])
            
            
            return HttpResponseRedirect('/vendors/items/')
    else:
        form = ItemForm() 

    return render(request,'admin/addEditItem.html', {
        'form': form,
    }) 
    
@login_required
def edit_item(request, item_id):
    i = Item.objects.get(pk=item_id)
    if request.method == 'POST': 
        form = ItemForm(request.POST)
            
        if form.is_valid(): 
            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
                
            i.update_item(form.cleaned_data['name'],
                             form.cleaned_data['description'],
                             form.cleaned_data['points'],
                             form.cleaned_data['inventory'],
                             image,
                             [])
            
            i.save()
            
            return HttpResponseRedirect('/vendors/items/')
    else:
        form = ItemForm(initial={'name':i.name,
                               'description':i.description,
                               'points':i.points,
                               'inventory':i.inventory,
                               'district_id':request.session['USER_ORGANIZATION_ID'],
                               'organization':i.get_organization_list(),
                               'id':i.id}) 

    return render(request,'admin/addEditItem.html', {
        'form': form,
    }) 
    
@login_required
def delete_item(request, item_id):
    Item.remove_item(item_id)
    
    return HttpResponseRedirect('/vendors/items/')  

@login_required
def order_history(request):
    order_list = []
    
    for order in Order.get_orders(request.user.id):
        item_list = []
        for oi in order.get_items():
            item = oi.item
            item_list.append({'id':item.id,
                          'name':item.name,
                          'points':item.points,
                          'inventory':item.inventory,
                          'vendor_name':'',#item.vendor.name,
                          'vendor_image_url':item.image_url()})
        
        order_list.append({'id':order.id,
                           'date_created':order.date_created.strftime("%m/%d/%Y"),
                           'item_list':item_list,
                           'order_total':order.order_total(),
                           'is_processed':order.is_processed})
    
    return render(request,"order_history.html", 
                              {'order_list':order_list,
                               }) 
    

@login_required
def list_orders(request):
    order_list = []
    
    for order in Order.get_all_orders(request.session['USER_ORGANIZATION_ID']):
        item_list = []
        for oi in order.get_items():
            item = oi.item
            item_list.append({'id':item.id,
                          'name':item.name,
                          'points':item.points,
                          'inventory':item.inventory,
                          
                          'image_url':item.image_url()})
        
        order_list.append({'id':order.id,
                           'date_created':order.date_created.strftime("%Y-%m-%d"),
                           'item_list':item_list,
                           'order_total':order.order_total(),
                           'student_name':order.user.get_full_name(),
                           'student_id':order.user.get_profile().get_student_profile().identifier,
                           'is_processed':order.is_processed})
    
    return render(request,"admin/manageOrders.html", 
                              {'order_list':order_list,
                               })     

@login_required
def process_order(request, order_id):
    Order.process_order(order_id)
    return HttpResponseRedirect('/orders/')

@login_required
def redeem(request):
    points_balance = PointsBalance.get_user_points_balance(request.user.id)
    cart = _get_cart(request)
    cart_total = 0
    for k,v in cart.items():
        cart_total+=v['points']
    
    item_list = []
    for item in Item.get_items_in_school(request.session['USER_ORGANIZATION_ID']):
        item_list.append({'id':item.id,
                          'name':item.name,
                          'points':item.points,
                          'inventory':item.inventory,
                          #'vendor_name':item.vendor.name,
                          'vendor_image_url':item.image_url()})
    
    return render(request,"redeem.html", 
                              {'item_list':item_list,
                               'points_balance':points_balance,
                               'cart':cart,
                               'cart_total':cart_total}) 
    
@login_required
def complete_order(request):
    cart = _get_cart(request)
    if len(cart):
        Order.create_order(request.user.id, cart.items())
        _delete_cart(request)
        
        return HttpResponseRedirect('/redeem/history/')
    
@login_required
def add_to_cart(request, item_id):
    
    cart = _get_cart(request)
    
    item = Item.objects.get(pk=item_id)
    cart[item_id] = {'id':item.id,
                      'name':item.name,
                      'vendor_name':'',#item.vendor.name,
                      'points':item.points}
    
    
    _save_cart(request, cart)
    return HttpResponseRedirect('/redeem/')

@login_required
def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    del cart[item_id]
    _save_cart(request, cart)
    return HttpResponseRedirect('/redeem/')


@login_required
def point_redemptions(request):
    #Get available schools
    school_filter = badges_views._setup_school_filter(request)
    
    data_set = {}
    if school_filter['selected_school_id']:
        student_list = []
        for sp in Organization.get_students(school_filter['selected_school_id']):
            student_list.append(sp.user.id)
            
        for oi in Order_Item.objects.filter(order__user__in=student_list, item__deleted=0, deleted=0, order__deleted=0):
            if oi.item_id not in data_set:
                data_set[oi.item_id] = {'name':oi.item.name,
                                       'vendor_name':'',#oi.item.vendor.name,
                                       'points':oi.item.points,
                                       'redemptions':0,
                                       'totalPointsSpent':0}
            
            data_set[oi.item_id]['redemptions'] += 1
            data_set[oi.item_id]['totalPointsSpent'] += oi.points
                              
    return render(request,"reports/pointRedemptions.html", 
                              {'school_list':school_filter['school_list'],
                               'selected_school_id':school_filter['selected_school_id'],
                               'data_set':data_set}) 

def _delete_cart(request):
    request.session['CART'] = {}
    
def _get_cart(request):
    if 'CART' not in request.session:
        request.session['CART'] = {}
    
    return request.session['CART']
    
def _save_cart(request, cart):
    request.session['CART'] = cart
    
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

def _setup_vendor_filter(request):
    vendor_list = []
    selected_vendor_id = _get_filter_value('vendor_id', request)
    
    results = Vendor.get_vendors()
                                
    for obj in results:
        vendor_list.append({'id':obj.id,'name':obj.__unicode__()})
   
    #Default to first vendor in list    
    if selected_vendor_id == 0:
        if(len(vendor_list)):
            selected_vendor_id = vendor_list[0]['id']
            request.session['SELECTED_vendor_id'] = selected_vendor_id
        else:
            school_list.append({'id':0,'name':'No vendors created.'})  
            
    return {'vendor_list':vendor_list,
            'selected_vendor_id':selected_vendor_id}
    
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