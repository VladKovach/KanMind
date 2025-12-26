from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanmind_app.models import Board


class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user

        return (
            obj.members.filter(pk=request.user.pk).exists() or obj.owner == request.user
        )


class IsBoardMember(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return Board.objects.filter(
                Q(owner=request.user) | Q(members=request.user)
            ).exists()
