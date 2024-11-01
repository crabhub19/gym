from django.contrib import admin
from .models import *  # Import the model



# Customizing the display of Accounts in the admin panel
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'join_date', 'activate_date', 'active')
    list_filter = ('role', 'active', 'join_date', 'activate_date')
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
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'amount', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('sender__username', 'transaction_id')
    ordering = ['-timestamp']

# Register the models and their custom admin views
admin.site.register(Accounts, AccountsAdmin)
admin.site.register(Transaction, TransactionAdmin)
# Register the other model 
admin.site.register(Profile)