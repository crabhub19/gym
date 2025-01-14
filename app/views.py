from django.shortcuts import render
from rest_framework import viewsets
from .serializer import *
from .models import *
# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer