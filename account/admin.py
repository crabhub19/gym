from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import *  # Import the model



# Customizing the display of Accounts in the admin panel
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class AccountsAdmin(ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'join_date', 'activate_date', 'active')
    list_filter = ('active', 'role', 'join_date', 'activate_date')
    search_fields = ('user__username', 'phone_number', 'role')
    
    # Restricting role assignment based on admin privileges
    def get_form(self, request, obj=None, **kwargs):
        form = super(AccountsAdmin, self).get_form(request, obj, **kwargs)
        
        if not request.user.is_superuser:  # Managers and non-admin users
            if hasattr(request.user, 'accounts') and request.user.accounts.role == 'manager':
                # Manager can create Trainer or Member accounts
                form.base_fields['role'].choices = [('trainer', 'Trainer'), ('member', 'Member')]
            else:
                # Normal users can only be assigned Member roles
                form.base_fields['role'].choices = [('member', 'Member')]
        return form
    
    # Auto-assigning admin privileges to managers
    def save_model(self, request, obj, form, change):
        if obj.role == 'manager':
            obj.user.is_staff = True  # Managers should have admin privileges
        obj.user.save()
        super().save_model(request, obj, form, change)


# Customizing the display of Transactions in the admin panel
class TransactionAdmin(ModelAdmin):
    list_display = ('display_sender', 'amount', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('sender__username', 'transaction_id')
    ordering = ['-timestamp']
    def display_sender(self, obj):
        return obj.sender if obj.sender else obj.sender_email
    display_sender.short_description = 'Sender'
    
class ProfileAdmin(ModelAdmin):
    list_display = ('get_username', 'age', 'weight', 'height', 'address')
    actions = ['delete_selected']  # Enable bulk delete action
    search_fields = ('account__user__username', 'account__user__email', 'bio')

    def get_username(self, obj):
        return obj.account.user.username
    get_username.short_description = 'Username'

    
class PaymentMethodAdmin(ModelAdmin):
    pass
# Register the models and their custom admin views
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Accounts, AccountsAdmin)
# Register the other model 
admin.site.register(Profile, ProfileAdmin)
admin.site.register(PaymentMethod,PaymentMethodAdmin)