from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer








class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()  # Base queryset for the model
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def perform_create(self, serializer):
        # Automatically set the sender to the logged-in user when creating a transaction
        serializer.save(sender=self.request.user)



class AccountViewSet(viewsets.ModelViewSet):
    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer