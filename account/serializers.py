from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import *



# Serializer for the Authentication model
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Override to use email for login
        username = User.objects.filter(email=attrs['username']).first()
        if username:
            attrs['username'] = username.username
        return super().validate(attrs)
# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # Explicitly define the email field

    class Meta:
        model = User
        fields = ['email', 'password','first_name', 'last_name']  # Don't expose the username field
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use email as username
        email = validated_data['email']
        cheak_email = User.objects.filter(email=email).exists()
        if cheak_email:
            raise serializers.ValidationError({"msg": "Email already exists in our community."})
        user = User.objects.create_user(
            username=email,  # Set email as username
            email=email,
            password=validated_data['password'],
            is_active=False
        )
        return user
    
# Serializer for the Account model
class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Use the updated UserSerializer

    class Meta:
        model = Accounts
        fields = ['user','phone_number']

    def create(self, validated_data):
        # Extract the user data
        user_data = validated_data.pop('user')
        # Create a new User instance
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        # Create the Account instance and link it to the user
        account = Accounts.objects.create(user=user, **validated_data)
        Profile.objects.create(account=account)
        return account

# Serializer for the Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'  # Include all fields in the Transaction model

# Serializer for the Profile model
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'  # Include all fields in the Profile model
