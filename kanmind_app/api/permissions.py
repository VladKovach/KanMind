from rest_framework import permissions


class IsOwnerOrMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # owner check
        print("obj.owner = ", obj.owner)
        if obj.owner == request.user:
            return True

        # member check
        return obj.members.filter(pk=request.user.pk).exists()
