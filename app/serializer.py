from rest_framework import serializers
from .models import *

class CourseSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Course
        fields = 'name','description','thumbnail_url','price','id'
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    