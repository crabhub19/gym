from rest_framework import viewsets,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from .permissions import IsAdminOrReadOnly

# for sending mails and generate token
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .utils import TokenGenerator,generate_token










class CustomTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Check if user with the given username exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "email not found.",'target':'email'}, status=status.HTTP_404_NOT_FOUND)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Incorrect password
            return Response({"detail": "incorrect password.",'target':'password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)








class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()  # Base queryset for the model
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def perform_create(self, serializer):
        # Automatically set the sender to the logged-in user when creating a transaction
        serializer.save(sender=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all()  # Admin sees all
        return Transaction.objects.filter(sender=user)  # Users see only their own transactions



class AccountViewSet(viewsets.ModelViewSet):
    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer
    def perform_create(self, serializer):
        # Get the username from the validated data
        user_data = serializer.validated_data['user']
        username = user_data.get('email')  # Using get() to avoid KeyError
        # Check if an inactive user with the same username exists
        inactive_user = User.objects.filter(username=username, is_active=False).first()
        if inactive_user:
            inactive_user.delete()  # Delete the inactive user
        account = serializer.save()
        self.send_verification_email(account)
    def send_verification_email(self, account):
        user = account.user
        token = generate_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(self.request).domain
        verification_link = f"http://{current_site}/account/accounts/verify-email/{uid}/{token}/"

        # Send email for verification
        mail_subject = 'Activate your account'
        mail_message = render_to_string('account/verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': uid,
            'token': token,
            'verification_link': verification_link,
        })
        print(mail_message)
        send_mail(mail_subject, mail_message, settings.DEFAULT_FROM_EMAIL, [user.email])
    @action(detail=False, methods=['get'], url_path='verify-email/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def verify_email(self, request, uidb64=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid Token or user not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Email successfully verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]





class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    #  Custom action to fetch the logged-in user's profile
    @action(detail=False, methods=['get'], url_path='me')
    def my_profile(self, request):
        try:
            # Fetch the profile of the logged-in user
            profile = Profile.objects.get(account__user=request.user)
        except Profile.DoesNotExist:
            # If no profile exists, raise a NotFound error
            raise NotFound(detail="Profile not found for the logged-in user.")
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    def get_object(self): 
        try: 
            profile = Profile.objects.get(account__user=self.request.user) 
            return profile 
        except Profile.DoesNotExist: 
            raise NotFound(detail="Profile not found for the logged-in user.")