from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

# Create a router and register the TransactionViewSet
router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'users', UserViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'paymentMethod', PaymentMethodViewSet)
router.register(r'contractUs', ContractUsViewSet)
router.register(r"post", PostViewSet)

# Include the router URLs
urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs under the /api/ path
        # Auth-related routes
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('api/validate-reset-uuid/', ValidatePasswordResetUUIDView.as_view(), name='validate-reset-uuid'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]

