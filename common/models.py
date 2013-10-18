from django.db import models
from django_extensions.db.fields import *
from django.contrib.auth.models import User

class CustomUUIDField(UUIDField):
    def pre_save(self, model_instance, add):
        if self.auto and add and (model_instance.id == '' or model_instance.id is None):
            value = unicode(self.create_uuid())
            setattr(model_instance, self.attname, value)
            return value
        else:
            value = super(UUIDField, self).pre_save(model_instance, add)
            if self.auto and not value:
                value = unicode(self.create_uuid())
                setattr(model_instance, self.attname, value)
        return value
          
class BaseModel(models.Model):
    id = CustomUUIDField(primary_key=True)
    created_by = models.CharField(max_length=36)
    date_created = CreationDateTimeField()
    updated_by = models.CharField(max_length=36)
    date_updated = ModificationDateTimeField()
    deleted = models.BooleanField(default=False)   
    
    def save(self, *args, **kwargs): 
        super(BaseModel, self).save(*args, **kwargs)
        
    def _safe_delete(self):
        self.deleted = 1
        self.save()
        
    def safe_delete(self):
        sub_objects = CollectedObjects()
        self._collect_sub_objects(sub_objects)
        
        cls_list = sub_objects.keys()
        for cls in cls_list:
            items = sub_objects[cls].items()
            for pk, instance in items:
                if pk != self.id:
                    try:
                        instance._safe_delete()
                    except NameError:
                        pass
        
        self._safe_delete()
                    
    class Meta:
        abstract = True
        
