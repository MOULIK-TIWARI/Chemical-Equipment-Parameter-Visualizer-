from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, RegisterView, LogoutView, DatasetViewSet

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Router URLs
    path('', include(router.urls)),
]
