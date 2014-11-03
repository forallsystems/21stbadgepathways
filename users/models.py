from django.db import models
from django.contrib.auth.models import User, Group
from common.models import *
from organizations.models import *
from django.db.models.signals import post_save
from datetime import date
from django.db.models import Q



class UserProfile(BaseModel):
    user = models.OneToOneField(User)
    phone_number = models.CharField(max_length=256)
    
    def get_role(self):
        for g in self.user.groups.all():
            if g.id == Role.STUDENT:
                return Role.STUDENT
            elif g.id == Role.SCHOOLADMIN:
                return Role.SCHOOLADMIN
            elif g.id == Role.DISTRICTADMIN:
                return Role.DISTRICTADMIN
            
        raise Exception('Unknown role')
    
    
    def get_student_profile(self):
        try:
            return StudentProfile.objects.get(user=self.user)
        except:
            sp = StudentProfile(user=self.user)
            sp.save()
            return sp
    
class StudentProfile(BaseModel):
    user = models.OneToOneField(User)
    identifier = models.CharField(max_length=256)
    parent_email = models.EmailField(max_length=256,blank=True)
    birth_date = models.DateField(blank=True,null=True)
    gradelevel = models.ForeignKey(GradeLevel, blank=True, null=True)
    external_id = models.CharField(max_length=256, blank=True, null=True)
    
    def get_age(self):
        if self.birth_date:
            born = self.birth_date
            today = date.today()
            try: # raised when birth date is February 29 and the current year is not a leap year
                birthday = born.replace(year=today.year)
            except ValueError:
                birthday = born.replace(year=today.year, day=born.day-1)
            if birthday > today:
                return today.year - born.year - 1
            else:
                return today.year - born.year
        
        return 0
    
    @staticmethod
    def find_student(student_id,username):
        sp_results = StudentProfile.objects.filter(Q(deleted=0),Q(identifier=student_id)|Q(user__username=username))
        
        for sp in sp_results:
            return sp.user
        
        return None
        
    
    @staticmethod
    def create_student(username, email, password, first_name, last_name, organization_id, identifier, gradelevel, birth_date):
        user = User.objects.create_user(username, email,password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        user.groups.add(Role.STUDENT)
        
        user_to_org = Organization_User(user=user,
                                        organization_id=organization_id)
        user_to_org.save()
        
        sp = user.get_profile().get_student_profile();
        sp.identifier = identifier
        sp.gradelevel = gradelevel
        sp.birth_date = birth_date
        sp.save()
        
        return user
    
    def update_student(self, username, email, password, first_name, last_name, organization_id, identifier, gradelevel, birth_date):
        self.user.first_name = first_name
        self.user.last_name = last_name
        if email:
            self.user.email = email
        self.user.username = username
        self.user.set_password(password)
        self.user.save()
        
        self.move_student(organization_id)
        
        self.identifier = identifier
        self.gradelevel = gradelevel
        self.birth_date = birth_date
        self.save()
    
    def get_school(self):
        for user_to_org in Organization_User.objects.filter(user=self.user,deleted=0):
            return user_to_org.organization
        
        return None
    
    def move_student(self, organization_id):
        for user_to_org in Organization_User.objects.filter(user=self.user,deleted=0):
            user_to_org.organization_id = organization_id
            user_to_org.save()
        
class Role(Group):
    
    STUDENT = 1
    SCHOOLADMIN = 2
    DISTRICTADMIN = 3
    
    class Meta:
        proxy = True    
        
class LogInHistory(BaseModel):
    user = models.ForeignKey(User)
    date = models.DateTimeField(blank=True,null=True)
    ip = models.CharField(max_length=15)
   
    @staticmethod
    def getLastLoginDate(user_id):
        try:
            rec = LogInHistory.objects.only('date').filter(user=user_id, deleted=0).order_by('-date')[0]
           
            return rec.date.strftime('%m/%d/%Y')
           
        except:
            return 'N/A'
        
        
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)