from rest_framework import permissions


class IsCurrentChar(permissions.BasePermission):

     def has_object_permission(self, request, view, obj):
         return request.user.current_char == obj

class HasCurrentChar(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.current_char is not None
