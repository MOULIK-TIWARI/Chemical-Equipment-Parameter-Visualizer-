"""
Custom permission classes for the Chemical Equipment Analytics API.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a dataset to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the dataset
        return obj.uploaded_by == request.user


class IsDatasetOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a dataset to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the owner can access their dataset
        return obj.uploaded_by == request.user
