from rest_framework import viewsets,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import *
from .serializers import *

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
    def perform_create(self, serializer):
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
        message = render_to_string('account/verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': uid,
            'token': token,
            'verification_link': verification_link,
        })
        print(message)
        # send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    @action(detail=False, methods=['get'], url_path='verify-email/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def verify_email(self, request, uidb64=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'msg': 'Invalid Token or user not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'msg': 'Email successfully verified.'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)