from badges.models import *
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

class PathwayCategoryAdmin(admin.ModelAdmin):
    fields = ['name',]
    list_display = ('name',)


admin.site.register(PathwayCategory,PathwayCategoryAdmin)