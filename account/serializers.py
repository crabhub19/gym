from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from app.serializer import *
from .models import *


# Serializer for the Authentication model
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Override to use email for login
        user = User.objects.filter(email=attrs['username']).first()
        if user:
            attrs['username'] = user.username
        return super().validate(attrs)
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (like admin status)
        token['is_staff'] = user.is_staff
        return token

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # Explicitly define the email field
    class Meta:
        model = User
        fields = ['id','email', 'password','first_name', 'last_name']  # Don't expose the username field
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'read_only': True} # Make email read-only
            }

    def create(self, validated_data):
        # Use email as username
        email = validated_data['email']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        cheak_email = User.objects.filter(email=email).exists()
        if cheak_email:
            raise serializers.ValidationError({"detail":"Email already exists."})
        user = User.objects.create_user(
            username=email,  # Set email as username
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=validated_data['password'],
            is_active=False
        )
        return user
    
# Serializer for the Account model
class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Use the updated UserSerializer
    course_name = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),  # Allows users to select a course by its primary key
        required=False,  # Course is optional
        allow_null=True  # Allows null if no course is selected
    )
    course_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Accounts
        fields = ['id','user','phone_number','role','active','course_name','course_details']
        extra_kwargs = {
            'role': {'read_only': True},
            'active': {'read_only': True},
        }
    def get_course_details(self, obj):
        if obj.course_name:
            return CourseSerializer(obj.course_name).data
    def create(self, validated_data):
        # Extract the user data
        user_data = validated_data.pop('user')
        # Extract course_name from validated data
        course_name = validated_data.pop('course_name', None)
        # Create a new User instance
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        # Create the Account instance and link it to the user
        account = Accounts.objects.create(user=user, course_name=course_name, **validated_data)
        Profile.objects.create(account=account)
        return account

# Serializer for the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'  # Include all fields in the Transaction model


# Serializer for the PaymentMethod model
class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_method_image = serializers.SerializerMethodField()
    class Meta:
        model = PaymentMethod
        fields = '__all__'  # Include all fields in the PaymentMethod model

    def get_payment_method_image(self, obj):
        if obj.payment_method_image:
            return obj.payment_method_image.url

# Serializer for the Profile model
class ProfileSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    profile_picture_url = serializers.SerializerMethodField()
    followers = serializers.StringRelatedField(many=True)
    class Meta:
        model = Profile
        fields = ['id','account', 'profile_picture','profile_picture_url','followers', 'bio', 'about', 'age', 'weight', 'height', 'address','gender']
        
    def update(self, instance, validated_data):
        account_data = validated_data.get('account', {})
        user_data = account_data.get('user', {})
        # Handle user data
        if user_data:
            user = instance.account.user  # Assuming Profile has a related Account
            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()
            
        # Handle account data, including phone number
        if 'phone_number' in account_data:
            instance.account.phone_number = account_data['phone_number']
            instance.account.save()
            
        # Handle other account and profile data
        for field, value in validated_data.items():
            if field != 'account':  # Don't overwrite the account object again
                setattr(instance, field, value)
        instance.save()

        return instance
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None  # Return None if no profile picture exists


class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.ReadOnlyField()
    author = ProfileSerializer(read_only=True)
    post_image_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    def get_post_image_url(self, obj):
        if obj.post_image:
            return obj.post_image.url
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            profile = request.user.accounts.profile  # Assuming this relationship exists
            return obj.post_likes.filter(profile=profile).exists()
        return False
    class Meta:
        model = Post
        fields = 'id','author','content','post_image','post_image_url','like_count','is_liked','created_at'
class PostLikeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = PostLike
        fields = 'id','post','profile','created_at'



class ContractUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractUs
        fields = '__all__'