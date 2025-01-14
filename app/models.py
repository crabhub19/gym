from django.db import models
from .baseModel import BaseModel
from cloudinary.models import CloudinaryField

# Create your models here.

class Course(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail =CloudinaryField("course_thumbnail",folder='course_thumbnail',blank=True,null=True)
    price = models.IntegerField()
    
    def __str__(self):
        return self.name