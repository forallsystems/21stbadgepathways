from django.db import models
from common.models import *
from organizations.models import *
from store.models import *
from django.contrib.auth.models import User
from django.core.cache import cache

#A collection of badges
class System(BaseModel):
    name =  models.CharField(max_length=256)
    issuer_name =  models.CharField(max_length=256)
    issuer_org =  models.CharField(max_length=256)
    issuer_contact =  models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name
    
    @staticmethod
    def get_default_system():
        for system in System.objects.filter(deleted=0):
            return system
        
        #If no system in the DB, create a default system
        system = System(name='Default', issuer_name='Forall Systems',issuer_org='Forall Systems', issuer_contact='')
        system.save()
        return system
    
class Badge(BaseModel):
    system = models.ForeignKey(System)
    name =  models.TextField()
    version =  models.CharField(max_length=20)
    description = models.TextField(blank=True)
    criteria = models.TextField(blank=True)
    image = models.FileField(blank=True,null=True,upload_to='files/badges',max_length=255)
    
    is_active = models.BooleanField(default=True)
    allow_send_obi = models.BooleanField(default=True)
    identifier = models.CharField(max_length=256, blank=True)
    points = models.IntegerField(default=0)
    sort_order = models.IntegerField(default=0)
    years_valid = models.IntegerField(default=0) #from date issued
    weight = models.IntegerField(default=0)
    
    gradelevels = models.ManyToManyField(GradeLevel, blank=True, null=True, through="Badge_GradeLevel")
    
    @staticmethod
    def get_badge_by_identifier(identifier):
        if identifier:
            for badge in Badge.objects.filter(deleted=0,identifier=identifier):
                return badge
        return None
    
    def get_mapped_pathway_names(self):
        names = ""
        for pb in Pathway_Badge.objects.filter(badge=self,deleted=0, pathway__deleted=0):
            if names != "":
                names+=", "
            names += pb.pathway.name
        return names
    
    def get_mapped_pathway_list(self):
        pathwayList = []
        for pb in Pathway_Badge.objects.filter(badge=self,deleted=0, pathway__deleted=0):
            pathwayList.append(pb.pathway_id)
        return pathwayList
    
    @staticmethod
    def get_badges(include_inactive=False):
        if include_inactive:
            return Badge.objects.filter(deleted=0).exclude(identifier__exact='').order_by('name')
        else:
            return Badge.objects.filter(deleted=0,is_active=1).exclude(identifier__exact='').order_by('name')
    
    @staticmethod
    def create_badge(identifier,name,description,criteria,image,is_active,years_valid,weight,points,allow_send_obi,gradelevels):
         b = Badge(system=System.get_default_system(),
                   identifier=identifier,
                   name=name,
                   description=description,
                   criteria=criteria,
                   image=image,
                   is_active=is_active,
                   years_valid=years_valid,
                   weight=weight,
                   points=points,
                   allow_send_obi=allow_send_obi)
         b.save()
         
         for gradelevel in gradelevels:
             bg = Badge_GradeLevel(badge=b, gradelevel=gradelevel)
             bg.save()
             
         return b
             
    def update_badge(self,identifier,name,description,criteria,image,is_active,years_valid,weight,points,allow_send_obi,gradelevels):
        self.identifier = identifier
        self.name = name
        self.description = description
        self.criteria = criteria
        if image:
            self.image = image
        self.is_active = is_active
        self.years_valid = years_valid
        self.weight = weight
        self.points = points
        self.allow_send_obi = allow_send_obi
        
        for g in Badge_GradeLevel.objects.filter(badge=self,deleted=0):
            g.deleted=1
            g.save()
        
        for gradelevel in gradelevels:
             bg = Badge_GradeLevel(badge=self, gradelevel=gradelevel)
             bg.save()
             
    @staticmethod
    def copy_badge(badge_id):
        ob = Badge.objects.get(pk = badge_id)
        b = Badge(system=System.get_default_system(),
                   identifier=ob.identifier,
                   name=ob.name + " (copy)",
                   description=ob.description,
                   criteria=ob.criteria,
                   image=ob.image,
                   is_active=ob.is_active,
                   years_valid=ob.years_valid,
                   weight=ob.weight,
                   points=ob.points,
                   allow_send_obi=ob.allow_send_obi)
        b.save()
        
        for g in Badge_GradeLevel.objects.filter(badge=badge_id,deleted=0):
            bg = Badge_GradeLevel(badge=b, gradelevel=g.gradelevel)
            bg.save()
            
        return b
                
    @staticmethod
    def delete_badge(badge_id):
        b = Badge.objects.get(pk = badge_id)
        b.deleted=1
        b.save()
        #TODO DELETE AWARDS!!!
    
    def image_url(self):
        url = None
        if(self.image):
            url = self.image.url
        return url
    
    def assigned_grades(self):
        list = ""
        for bg in Badge_GradeLevel.objects.filter(badge=self,deleted=0):
            if list != "":
                list+=", "
            list += bg.gradelevel.short_name()
        return list
    
    def get_gradelevel_list(self):
        list = {}
        for bg in Badge_GradeLevel.objects.filter(badge=self,deleted=0):
            list[bg.gradelevel.id] = bg.gradelevel.__unicode__()
        return list
        
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __unicode__(self):
        return self.name
    
class Badge_GradeLevel(BaseModel):
    badge = models.ForeignKey(Badge)
    gradelevel = models.ForeignKey(GradeLevel)   
    

    
class Award(BaseModel):
    badge = models.ForeignKey(Badge)
    user = models.ForeignKey(User)
    
    points = models.IntegerField(default=0)
    comments = models.TextField(blank=True)
    expiration_date = models.DateField(blank=True,null=True)
    
    external_id = models.TextField(default=0)
    
    @staticmethod
    def award_exists_by_external_id(external_id):
        if Award.objects.filter(external_id=external_id).count():
            return True
        return False
    @staticmethod
    def award_exists(user_id, badge_id):
        if Award.objects.filter(badge_id=badge_id, user_id=user_id).count():
            return True
        return False
    
    @staticmethod
    def get_user_awards_by_pathway(user_id, pathway_id):
        badge_list = Pathway.get_related_badge_list(pathway_id)
        pathway = Pathway.objects.get(pk=pathway_id)
        pb = pathway.get_pathway_badge()
        badge_list.append(pb.id)
        badgeMap = {}
        award_list = Award.objects.filter(user=user_id,
                                    deleted=0,
                                    badge__in=badge_list)
        
        #if they earned all awards, issue pathway badge
        for a in award_list:
            badgeMap[a.badge_id] = True
        
        if len(badgeMap) == len(badge_list)-1:
            pathway = Pathway.objects.get(pk=pathway_id)
            pathway_badge = pathway.get_pathway_badge()
            if not Award.award_exists(user_id, pathway_badge.id):
                Award.create_award(user_id,pathway_badge.id)
            
        
        return award_list
    @staticmethod
    def get_user_awards(user_id):
        return Award.objects.filter(user=user_id,
                                    deleted=0).order_by('-date_created')
        
    @staticmethod
    def get_user_num_awards(user_id):
        return Award.objects.filter(user=user_id,
                                    deleted=0).count()
                                    
    @staticmethod
    def get_awards_in_badge_list(user_id, badge_list):
        return Award.objects.filter(user=user_id,
                                    badge__in=badge_list,
                                    deleted=0)
        
    @staticmethod
    def delete_award(award_id):
        award = Award.objects.get(pk=award_id)
        award.deleted = 1
        award.save()
        
    @staticmethod
    def delete_award_by_external_id(external_id):
        for award in Award.objects.filter(external_id=external_id, deleted=0):
            award.deleted=1
            award.save()
        
        for evidence in Evidence.objects.filter(deleted=0, award=award):
            evidence.deleted=1
            evidence.save()
        
    @staticmethod
    def create_award(user_id,badge_id, comments=""):
        badge= Badge.objects.get(pk=badge_id)
        award = Award(badge=badge,user_id=user_id,points=badge.points, comments=comments)
        award.save()
        
        PointsBalance.increase_balance(user_id, badge.points)
        
        return award
    
class Evidence(BaseModel):      
    award = models.ForeignKey(Award)  
    file = models.FileField(upload_to='files/awards/evidence')  
    hyperlink = models.TextField(blank=True,null=True)
    name =  models.CharField(max_length=256)
    
    @staticmethod
    def create_evidence(award_id, fileObj, hyperlink, name):
        e = Evidence(award_id=award_id, hyperlink=hyperlink, name=name)
        if fileObj:
            e.file = fileObj
        return e.save()
    
class PathwayCategory(BaseModel):
    name =  models.CharField(max_length=256)
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return self.name
        
class Pathway(BaseModel):
    pathwaycategory = models.ForeignKey(PathwayCategory)
    name =  models.CharField(max_length=256)
    description = models.TextField(blank=True)
    organizations = models.ManyToManyField(Organization, blank=True, null=True, through='Pathway_Organization', related_name="pathway_organizations")
    badges = models.ManyToManyField(Badge, through='Pathway_Badge', related_name="pathway_badges")
    users = models.ManyToManyField(User, through='Pathway_User', related_name="pathway_users")
    sort_order = models.IntegerField(default=0)
    
    @staticmethod
    def get_user_pathways(user_id):
        return Pathway.objects.filter(deleted=0,
                                      users__in=[user_id,],
                                      pathway_user__deleted=0).order_by('pathway_user__sort_order','sort_order','name')
        
    @staticmethod
    def get_user_pathway_list(user_id):
        pathway_list = []
        for pathway in Pathway.get_user_pathways(user_id):
            pathway_badge_list = Award.get_awards_in_badge_list(user_id, Pathway.get_related_badge_list(pathway.id))
            total_points = 0
            award_total = 0
            badgeMap = {}
            for award in pathway_badge_list:
                total_points += award.points
                badgeMap[award.badge_id] = True
            
            award_total = len(badgeMap)
            # award_total = 0
            
            
            total_badges = pathway.get_num_badges()
            if total_badges:
                percent_complete = int((float(award_total) / float(total_badges)) * 100.0)
            else:
                percent_complete = 0
            pathway_list.append({'id':pathway.id,
                                'name':pathway.name,
                                'award_total':award_total,
                                'percent_complete':percent_complete,
                                'total_badges':total_badges,
                                'total_points':total_points,
                                'badge_image_url':pathway.badge_image_url(),
                                })
        return pathway_list
            
    @staticmethod
    def add_user_pathway(user_id, pathway_id):
        if Pathway_User.objects.filter(user=user_id, pathway=pathway_id,deleted=0).count() == 0:
            pu = Pathway_User(pathway_id=pathway_id,
                              user_id=user_id,
                              sort_order=Pathway_User.objects.filter(user=user_id).count()+1)
            pu.save()   
            
    @staticmethod
    def delete_user_pathway(user_id, pathway_id):
        for pu in Pathway_User.objects.filter(user=user_id, pathway=pathway_id,deleted=0):
            pu.deleted=1
            pu.save()
    
    @staticmethod
    def get_pathways(organization_id=None, exclude_list=None):
        if organization_id:
            
            if exclude_list:
                print organization_id
                return Pathway.objects.filter(deleted=0).exclude(id__in=exclude_list).order_by('sort_order','name').distinct()
            else:
                return Pathway.objects.filter(deleted=0).order_by('sort_order','name').distinct()
        else:
            return Pathway.objects.filter(deleted=0).order_by('sort_order','name')
    
    @staticmethod
    def get_pathway_list(organization_id=None, exclude_list=None):
        pathway_list = []
        for pathway in Pathway.get_pathways(organization_id, exclude_list=exclude_list):
            pathway_list.append({'id':pathway.id,
                                'name':pathway.name,
                                'description':pathway.description,
                                'badge_image_url':pathway.badge_image_url(),
                                'category':pathway.pathwaycategory.name,
                                'num_badges':pathway.get_num_badges(),
                                'schools':pathway.assigned_schools()})
        return pathway_list
    
    @staticmethod
    def create_pathway(name,pathwaycategory,description,organization_list,badge_name,badge_description,badge_criteria,badge_image,badge_points):
        p = Pathway(name=name,
                    pathwaycategory=pathwaycategory,
                    description=description,
                    sort_order=Pathway.get_num_pathways()+1)
        p.save()
        
        for organization_id in organization_list:
            po = Pathway_Organization(pathway=p, organization_id = organization_id)
            po.save()
            
        b = Badge.create_badge('', badge_name, badge_description, badge_criteria, badge_image, True, 99, 0, badge_points, False, [])
    
        pb = Pathway_Badge(pathway=p,
                           badge=b,
                           is_pathway_badge=True,
                           sort_order=0)
        pb.save()
        
    def update_pathway(self,name,pathwaycategory,description,organization_list,badge_name,badge_description,badge_criteria,badge_image,badge_points):
        self.name = name
        self.pathwaycategory = pathwaycategory
        self.description = description
        
        for po in Pathway_Organization.objects.filter(pathway=self,deleted=0):
            po.deleted=1
            po.save()
        
        for organization_id in organization_list:
            po = Pathway_Organization(pathway=self, organization_id = organization_id)
            po.save()
            
        pb = self.get_pathway_badge()
            
        pb.update_badge('',badge_name, badge_description, badge_criteria, badge_image, True, 99, 0, badge_points, False, [])
        pb.save()
        self.save()
        
    @staticmethod
    def copy_pathway(pathway_id):
        op = Pathway.objects.get(pk=pathway_id)
        p = Pathway(name=op.name + " (copy)",
                    pathwaycategory=op.pathwaycategory,
                    description=op.description,
                    sort_order=op.sort_order)
        p.save()
        
        opb = op.get_pathway_badge()
        b = Badge.copy_badge(opb.id)
        
        pb = Pathway_Badge(pathway=p,
                           badge=b,
                           is_pathway_badge=True,
                           sort_order=0)
        pb.save()
        
        for opo in Pathway_Organization.objects.filter(pathway=op,deleted=0):
            po = Pathway_Organization(pathway=p, organization_id = opo.organization_id)
            po.save()
            
        return p
        
    @staticmethod
    def delete_pathway(pathway_id):
        p = Pathway.objects.get(pk=pathway_id)
        p.deleted=1
        p.save()
        #DELETE RELATED ITEMS!!!
        
    def get_pathway_badge(self):
        for pb in Pathway_Badge.objects.filter(pathway=self,is_pathway_badge=True,deleted=0):
            return pb.badge
        
        return None
    
    @staticmethod
    def get_num_pathways():
        return Pathway.objects.filter().count()
    
    def get_num_badges(self):
        return Pathway_Badge.objects.filter(pathway=self,is_pathway_badge=False,deleted=0,badge__is_active=1).count()
    
    @staticmethod
    def get_related_badges(pathway_id):
        return Pathway_Badge.objects.filter(pathway=pathway_id, is_pathway_badge=False,deleted=0,badge__is_active=1).order_by('sort_order')
    
    @staticmethod
    def get_related_badge_list(pathway_id):
        
        badge_list = cache.get('GET_RELATED_BADGE_LIST_'+pathway_id)
        if badge_list is None:
            badge_list = []
        else:
            return badge_list

        for pb in Pathway.get_related_badges(pathway_id):
            badge_list.append(pb.badge_id)
            
        cache.set('GET_RELATED_BADGE_LIST_'+pathway_id, badge_list, 86400)
            
        return badge_list
    
    @staticmethod
    def add_badge(pathway_id, badge_id):
        p = Pathway.objects.get(pk=pathway_id)
        pb = Pathway_Badge(pathway=p,
                           badge_id=badge_id,
                           is_pathway_badge=False,
                           sort_order=p.get_num_badges()+1)
        pb.save()
        
    @staticmethod
    def delete_badge(pathway_id, badge_id):
        for pb in Pathway_Badge.objects.filter(pathway=pathway_id, badge=badge_id, deleted=0):
            pb.deleted=1
            pb.save()
        
    @staticmethod
    def update_badge_sortorder(pathway_id, badge_id, sort_order):
        for pb in Pathway_Badge.objects.filter(pathway=pathway_id, badge=badge_id, deleted=0):
            pb.sort_order=sort_order
            pb.save()
    
    def get_organization_list(self):
        org_list = {}
        for po in Pathway_Organization.objects.filter(pathway=self,deleted=0):
            org_list[po.organization_id] = po.organization.__unicode__()
        return org_list
        
    def assigned_schools(self):
        list = ""
        for pu in Pathway_Organization.objects.filter(pathway=self,deleted=0):
            if list != "":
                list+=", "
            list += pu.organization.__unicode__()
        return list
    
    def badge_image_url(self):
        url = None
        
        for pb in Pathway_Badge.objects.filter(pathway=self,is_pathway_badge=True,deleted=0):
            if(pb.badge.image):
                url = pb.badge.image.url
                
        return url
    
    def __unicode__(self):
        return self.name
    
class Pathway_Badge(BaseModel):
    pathway = models.ForeignKey(Pathway)
    badge = models.ForeignKey(Badge)
    is_pathway_badge = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
class Pathway_User(BaseModel):
    pathway = models.ForeignKey(Pathway)
    user = models.ForeignKey(User)
    sort_order = models.IntegerField(default=0)
    
class Pathway_Organization(BaseModel):
    pathway = models.ForeignKey(Pathway)
    organization = models.ForeignKey(Organization)
