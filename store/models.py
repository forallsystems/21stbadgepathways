from django.db import models
from django.contrib.auth.models import User
from common.models import *
from organizations.models import *

class PointsBalance(BaseModel):
    user = models.ForeignKey(User)
    points = models.IntegerField(default=0)
    
    @staticmethod
    def get_user_points_balance(user_id):
        for pb in PointsBalance.objects.filter(deleted=0,user=user_id):
            return pb.points
        
        pb = PointsBalance(user_id=user_id, points=0)
        pb.save()
        return pb.points
    
    @staticmethod
    def decrease_balance(user_id, points):
        for pb in PointsBalance.objects.filter(deleted=0,user=user_id):
            pb.points -= points
            pb.save()
            
    @staticmethod
    def increase_balance(user_id, points):
        PointsBalance.get_user_points_balance(user_id)
        for pb in PointsBalance.objects.filter(deleted=0,user=user_id):
            pb.points += points
            pb.save()

   
class Vendor(BaseModel):
    name = models.CharField(max_length=256)
    image = models.FileField(blank=True,null=True,upload_to='files/order/vendor')
    
    @staticmethod
    def create_vendor(name, image=None):
        vendor = Vendor(name=name, image=image)
        vendor.save()
        return vendor
    
    @staticmethod
    def get_vendors():
        return Vendor.objects.filter(deleted=0)
    
    @staticmethod
    def delete_vendor(vendor_id):
        v = Vendor.objects.get(pk = vendor_id)
        v.deleted=1
        v.save()
        #TODO DELETE ITEMS!!!
    
    def total_items(self):
        return Item.objects.filter(vendor=self, deleted=0).count()
    
    def image_url(self):
        url = None
        if(self.image):
            url = self.image.url
        return url
    
    def __unicode__(self):
        return self.name
    
    
class Item(BaseModel):
    vendor = models.ForeignKey(Vendor,blank=True,null=True)
    name = models.CharField(max_length=256)
   
    description = models.TextField()
    points = models.IntegerField(default=0)
    inventory = models.IntegerField(default=0)
    image = models.FileField(blank=True,null=True,upload_to='files/order/item')
    organizations = models.ManyToManyField(Organization, through='Item_Organization')
    
    @staticmethod
    def get_items(vendor_id):
        return Item.objects.filter(deleted=0, vendor=vendor_id).order_by('name')
    
    @staticmethod
    def get_items_in_school(school_id):
        return Item.objects.filter(deleted=0, item_organization__organization=school_id,item_organization__deleted=0).order_by('name')
    
    @staticmethod
    def get_available_items(organization_id):
        return Item.objects.filter(deleted=0, 
                                   vendor__deleted=0,
                                   item_organization__organization_id=organization_id, 
                                   item_organization__deleted=0).order_by('vendor')
    
    @staticmethod
    def create_item(vendor_id,name,description,points,inventory,image,organization_list):
        i = Item(vendor_id=vendor_id, 
                 name=name,
                 description=description,
                 points=points,
                 image=image,
                 inventory=inventory)
        i.save()
        
        for organization_id in organization_list:
            io = Item_Organization(item=i, organization_id = organization_id)
            io.save()
            
        return i
    
    @staticmethod
    def remove_item(item_id):
        i = Item.objects.get(pk=item_id)
        i.deleted=1
        i.save()
    
    def update_item(self, name,description,points,inventory,image,organization_list):
        self.name = name
        self.description = description
        self.points= points
        self.inventory = inventory
        if image:
            self.image = image
        
        if len(organization_list):
            for io in Item_Organization.objects.filter(item=self,deleted=0):
                io.deleted=1
                io.save()
            
            for organization_id in organization_list:
                io = Item_Organization(item=self, organization_id = organization_id)
                io.save()
        
    def get_organization_list(self):
        org_list = {}
        for io in Item_Organization.objects.filter(item=self,deleted=0):
            org_list[io.organization_id] = io.organization.__unicode__()
        return org_list
    
    def image_url(self):
        url = None
        if(self.image):
            url = self.image.url
        return url
    
    def __unicode__(self):
        return self.name
    

class Item_Organization(BaseModel):
    item = models.ForeignKey(Item)
    organization = models.ForeignKey(Organization)
    
class Order(BaseModel):
    user = models.ForeignKey(User)
    items = models.ManyToManyField(Item, through='Order_Item')
    is_processed = models.BooleanField(default=False)
    
    @staticmethod
    def get_orders(user_id):
        return Order.objects.filter(user=user_id, deleted=0).order_by('-date_created')
    
    @staticmethod
    def get_all_orders(school_id):
        return Order.objects.filter(deleted=0,user__organization__id=school_id, 
                                             user__organization__deleted=0,).order_by('-date_created')
    
    @staticmethod
    def create_order(user_id, cart):
        order = Order(user_id=user_id)
        order.save()
        
        for k,v in cart:
            order.add_item(user_id, v['id'], v['points'])
            
    @staticmethod
    def process_order(order_id):
        order = Order.objects.get(pk=order_id)
        order.is_processed = True
        order.save()
        
    def add_item(self, user_id, item_id, points):
        i = Item.objects.get(pk=item_id)
        if i.inventory >= 1:
            i.inventory-=1
            i.save()
            
            oi = Order_Item(order=self, item_id=item_id, points=points)
            oi.save()
            
            PointsBalance.decrease_balance(user_id, points)
            
    def order_total(self):
        points = 0
        for oi in Order_Item.objects.filter(order=self,deleted=0):
            points+=oi.points
        return points    
    
    def get_items(self):
        return Order_Item.objects.filter(order=self, deleted=0)
    
class Order_Item(BaseModel):
    order = models.ForeignKey(Order)
    item = models.ForeignKey(Item)
    points = models.IntegerField(default=0)

    