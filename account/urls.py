from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *

# Create a router and register the TransactionViewSet
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'accounts', AccountViewSet)

# Include the router URLs
urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs under the /api/ path
        # Auth-related routes
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
