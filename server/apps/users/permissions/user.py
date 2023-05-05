from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view) -> bool:
        if request.method == "GET":
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_authenticated
