from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import *
# Register your models here.
class CourseAdmin(ModelAdmin):
    pass
admin.site.register(Course,CourseAdmin)