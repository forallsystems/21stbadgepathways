from django.db import models
from common.models import *
from mptt.models import MPTTModel

                  
class Organization(MPTTModel, BaseModel):
    name = models.CharField(max_length=256)
    
    TYPE_STATE = 0
    TYPE_REGION = 1
    TYPE_DISTRICT = 2
    TYPE_SCHOOL = 3
    
    type = models.IntegerField()
    type_label = models.CharField(max_length=256, blank=True)
    organization_id = models.CharField(max_length=256)
    
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    users = models.ManyToManyField(User, through='Organization_User')
    
    enable_store = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def update_organization(self,name,organization_id,enable_store):
        self.name=name
        self.organization_id = organization_id
        self.enable_store = enable_store
        self.save()
    
    @staticmethod
    def create_organization(parent_id, name, type, type_label,enable_store=0,organization_id=''):
        org = Organization(name=name,
                           type=type,
                           type_label=type_label,
                           enable_store=enable_store,
                           organization_id=organization_id,
                           parent_id=parent_id)
        org.save()
        return org
    
    @staticmethod   
    def get_user_organization(user_id):             
         results = Organization_User.objects.filter(user = user_id, deleted=0).order_by('organization__level')
         if(len(results) > 0):
             return results[0].organization
         
         return None  
     
    @staticmethod
    def get_schools(parent_id):
         return Organization.objects.filter(parent__id = parent_id, 
                                   type=Organization.TYPE_SCHOOL,
                                   deleted=0).order_by('name')
                                   
    @staticmethod
    def get_students(organization_id):
        from users.models import StudentProfile
        return StudentProfile.objects.select_related('gradelevel','user').filter(deleted=0,
                                             user__organization__id=organization_id, 
                                             user__organization__deleted=0,
                                             user__groups__id=1,
                                             user__is_active=1)
        
    @staticmethod
    def get_students_by_orgtype(organization_type_label):
        from users.models import StudentProfile
        if organization_type_label == 'All':
            return StudentProfile.objects.only('user__id','gradelevel__name','user__first_name','user__last_name','identifier').select_related('gradelevel','user').filter(deleted=0,
                                             user__organization__deleted=0,
                                             user__groups__id=1,
                                             user__is_active=1)
        else:
            return StudentProfile.objects.only('user__id','gradelevel__name','user__first_name','user__last_name','identifier').select_related('gradelevel','user').filter(deleted=0,
                                             user__organization__type_label=organization_type_label, 
                                             user__organization__deleted=0,
                                             user__groups__id=1,
                                             user__is_active=1)
    @staticmethod
    def get_districtadmins(organization_id):
        return User.objects.filter(organization__id=organization_id, 
                                   organization__deleted=0,
                                   groups__id=3,
                                   is_active=1)
        
    @staticmethod
    def get_schooladmins(organization_id):
        return User.objects.filter(organization__id=organization_id, 
                                   organization__deleted=0,
                                   groups__id=2,
                                   is_active=1)
        
    @staticmethod
    def remove_student(user_id):
        Organization.remove_user(user_id)
            
    @staticmethod
    def remove_user(user_id):
        for ou in Organization_User.objects.filter(user=user_id,
                                                   deleted=0):
            ou.deleted=1
            ou.save()
    
class Organization_User(BaseModel):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    
    
class GradeLevel(BaseModel):
    name = models.CharField(max_length=256)
    sort_order = models.IntegerField()  
    
    def __unicode__(self):
        return self.name
    
    def short_name(self):
        if self.name == "Transitional Kindergarten":
            return "TK"
        if self.name == "Kindergarten":
            return "K"
        if self.name == "Pre-K":
            return "Pre-K"
        return self.name.replace(" Grade","")
    

    
   