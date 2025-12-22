from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user

        return (
            obj.members.filter(pk=request.user.pk).exists() or obj.owner == request.user
        )
