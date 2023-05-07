from rest_framework import permissions


class InvitePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.id in (obj.target.id, obj.owner.id)
