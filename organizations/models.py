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
    enable_custom_login = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def init_settings(self):
        if not Organization_Settings.objects.filter(deleted=0, organization=self).count():
            os = Organization_Settings(organization=self)
            os.login_url = self.name.replace(" ","").lower()
            #make sure login_url is unique
            while(True):
                if Organization_Settings.objects.filter(deleted=0, login_url=os.login_url).count():
                    os.login_url = os.login_url+"_1"
                else:
                    break
            os.save()
            
            return os
        
        return Organization_Settings.objects.get(organization=self)
    
    def update_settings(self,login_url, primary_logo, login_text, login_text_background_color, login_text_color, header_color, background_color, text_color):
        settings = self.init_settings()
        
        settings.login_url = login_url
        if primary_logo:
            settings.primary_logo = primary_logo
            
        
        settings.login_text = login_text
        settings.login_text_background_color = login_text_background_color
        settings.login_text_color = login_text_color
        settings.header_color = header_color
        settings.background_color = background_color
        settings.text_color = text_color
        settings.save()
    
    def update_organization(self,name,organization_id,enable_store,enable_custom_login):
        self.name=name
        self.organization_id = organization_id
        self.enable_store = enable_store
        self.enable_custom_login = enable_custom_login
        self.save()
        
        if enable_custom_login:
            self.init_settings()
    
    @staticmethod
    def create_organization(parent_id, name, type, type_label,enable_store=0,enable_custom_login=0, organization_id=''):
        org = Organization(name=name,
                           type=type,
                           type_label=type_label,
                           enable_store=enable_store,
                           enable_custom_login=enable_custom_login,
                           organization_id=organization_id,
                           parent_id=parent_id)
        org.save()
        
        if enable_custom_login:
            org.init_settings()
        
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
    
    
class Organization_Settings(BaseModel):
    organization = models.ForeignKey(Organization)
    login_url = models.CharField(max_length=256, blank=True)
    primary_logo = models.FileField(blank=True,null=True,upload_to='files')
    login_text = models.TextField()
    login_text_background_color = models.CharField(max_length=7, default="#ef8300") 
    login_text_color = models.CharField(max_length=7, default="#FFFFFF") 
    header_color = models.CharField(max_length=7, default="#54839f") 
    background_color = models.CharField(max_length=7, default="#d5ecfa") 
    text_color = models.CharField(max_length=7, default="#333333") 
    
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
    

    
   