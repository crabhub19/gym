from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.utils import timezone
# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Accounts(BaseModel):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('trainer', 'Trainer'),
        ('manager', 'Manager'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one relationship with User
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    join_date = models.DateField(default=timezone.now)  # Join date field
    activate_date = models.DateField(null=True,blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
           # Fetch transaction history for this account
    def get_transaction_history(self):
        sent_transactions = self.user.sent_transactions.all()
        return {
            sent_transactions
        }


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'{self.sender} sent {self.amount}'
 
    class Meta:
        ordering = ['-timestamp']


class PaymentMethod(BaseModel):
    METHOD_CHOICES = [
        ('bkash', 'Bkash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('all', 'Bkash, Nagad, Rocket'),
    ]
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='bkash')
    description = models.TextField(blank=True, null=True)



class Profile(BaseModel):
    account = models.OneToOneField(Accounts, on_delete=models.CASCADE)  # One-to-one relationship with Account
    bio = models.TextField(blank=True)  # Bio field for the user
    profile_picture = CloudinaryField("profile_picture",blank=True,null=True)   # URL for Cloudinary
    cover_picture = CloudinaryField("cover_picture",blank=True,null=True)

    def __str__(self):
        return f"{self.account.user.username}'s Profile"