from organizations.models import *
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

class Organization_UserInline(admin.TabularInline):
    fields = ['organization','user','deleted']
    raw_id_fields = ("user",)
    model = Organization_User
    extra = 1   
    
class OrganizationAdmin(admin.ModelAdmin):#(MPTTModelAdmin):
    fields = ['name','parent','type','type_label','deleted']
    list_display = ('name','type','type_label')
    inlines = (Organization_UserInline,)
    search_fields = ['name',] 
    raw_id_fields = ("parent",)   
    
class GradeLevelAdmin(admin.ModelAdmin):
    fields = ['name','sort_order']
    list_display = ('name','sort_order')

admin.site.register(Organization,OrganizationAdmin)
admin.site.register(GradeLevel,GradeLevelAdmin)