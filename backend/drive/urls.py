"""
URL configuration for drive app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for ViewSets
router = DefaultRouter()
router.register(r'files', views.DriveNodeViewSet, basename='file')
router.register(r'trash', views.TrashViewSet, basename='trash')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', views.auth_login, name='auth-login'),
    path('auth/status/', views.auth_status, name='auth-status'),

    # ViewSet endpoints (files, folders, trash)
    path('', include(router.urls)),
]