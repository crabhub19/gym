import random
from rest_framework import viewsets,status
from rest_framework.permissions import *
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from .models import *
from .serializers import *
from .permissions import *
from .pagination import *


# for sending mails and generate token
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .utils import generate_token










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

#reset password
class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update PasswordReset entry
        reset_entry, created = PasswordReset.objects.get_or_create(user=user)
        if not created:
            reset_entry.uuid = str(random.randint(1000, 9999))  # Generate a new UUID
            reset_entry.created_at = now()
            reset_entry.save()
        send_mail("Password Reset Request", f'Your password reset code is: {reset_entry.uuid}', settings.DEFAULT_FROM_EMAIL, [user.email])
        

        return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)

class ValidatePasswordResetUUIDView(APIView):
    def post(self, request):
        uuid_code = request.data.get('uuid_code')

        if not uuid_code:
            return Response({'detail': 'UUID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_entry = PasswordReset.objects.get(uuid=uuid_code)
        except PasswordReset.DoesNotExist:
            return Response({'detail': 'Invalid or expired UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not reset_entry.is_valid():
            return Response({'detail': 'UUID has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'UUID is valid.'}, status=status.HTTP_200_OK)
class ResetPasswordView(APIView):
    def post(self, request):
        uuid_code = request.data.get('uuid_code')
        new_password = request.data.get('new_password')

        if not uuid_code or not new_password:
            return Response({'detail': 'UUID and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_entry = PasswordReset.objects.get(uuid=uuid_code)
        except PasswordReset.DoesNotExist:
            return Response({'detail': 'Invalid or expired UUID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not reset_entry.is_valid():
            return Response({'detail': 'UUID has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the password
        user = reset_entry.user
        user.set_password(new_password)
        user.save()

        # Delete the PasswordReset entry
        reset_entry.delete()

        return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)




#User viewset
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]
    @action(detail=False,methods=['post'])
    def changePassword(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect.','target':'old_password'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)
    




class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()  # Base queryset for the model
    serializer_class = TransactionSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [AllowAny()]  # Allow POST requests for any user
        elif self.request.method in ['GET', 'PATCH', 'PUT', 'DELETE']:
            return [IsAdminOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Automatically set the sender to the logged-in user when creating a transaction
        serializer.save(sender=self.request.user if self.request.user.is_authenticated else None)
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff:
    #         return Transaction.objects.all()  # Admin sees all
    #     return Transaction.objects.filter(sender=user)  # Users see only their own transactions



class AccountViewSet(viewsets.ModelViewSet):
    queryset = Accounts.objects.all()
    serializer_class = AccountSerializer
    def get_permissions(self):
        if self.request.method in ['GET', 'POST']:
            return [AllowAny()]
        elif self.request.method in ['PATCH', 'PUT','DELETE']:
            return [IsAuthenticated()]  # Use built-in permission for authenticated users
        return super().get_permissions()

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
            return render(request, 'account/email_verification_failed.html')

        if generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, 'account/email_verified_success.html')
        else:
            return render(request, 'account/email_verification_failed.html')


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAdminOrReadOnly]





class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.filter(account__user__is_active=True).order_by(
        models.Case(
            models.When(account__role='manager', then=0),
            models.When(account__role='trainer', then=1),
            models.When(account__role='member', then=2),
            default=3,
            output_field=models.IntegerField()
        )
    )
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = tenPagination
    #  Custom action to fetch the logged-in user's profile
    @action(detail=False, methods=['get','patch','delete'], url_path='me')
    def my_profile(self, request):
        try:
            # Fetch the profile of the logged-in user
            profile = Profile.objects.get(account__user=request.user)
        except Profile.DoesNotExist:
            # If no profile exists, raise a NotFound error
            raise NotFound(detail="Profile not found for the logged-in user.")
        if request.method == 'GET':
            # Serialize and return the profile data
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            # Partially update the profile with the provided data
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            # Delete the profile
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = tenPagination
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        # Use request.user to get the associated profile
        profile = self.request.user.accounts.profile  # Assuming this relationship exists
        serializer.save(author=profile)
    
    @action(detail=False, methods=['get','delete'])
    def my_posts(self, request):
        profile = request.user.accounts.profile  # Assuming this relationship exists

        if request.method == 'GET':
            posts = Post.objects.filter(author=profile).order_by('-created_at')
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)

        if request.method == 'DELETE':
            # Ensure a specific post ID is provided
            post_id = request.query_params.get('post_id')
            if not post_id:
                return Response({'error': 'Post ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                post = Post.objects.get(id=int(post_id), author=profile)
                post.delete()
                return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except Post.DoesNotExist:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def like(self, request, pk):
        post = get_object_or_404(Post,pk=pk)
        like,created = PostLike.objects.get_or_create(post=post,profile=request.user.accounts.profile)
        if not created:
            like.delete()
        return Response({'detail': 'Like toggled successfully.'}, status=status.HTTP_200_OK)
        

class ContractUsViewSet(viewsets.ModelViewSet):
    queryset = ContractUs.objects.all()
    serializer_class = ContractUsSerializer
    permission_classes = [IsAdminOrPostOnly]
    def perform_create(self, serializer):
        contractUs = serializer.save()
        self.send_contract_email(contractUs)
    def send_contract_email(self,contractUs):
        mail_subject = 'Contract Us'
        mail_message = render_to_string('account/contractus_email.html', {
            'contractUs': contractUs,
        })
        send_mail(
            subject=mail_subject,
            message=mail_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['3xbishal@gmail.com']
        )

        
    