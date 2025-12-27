from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanmind_app.models import Board


class IsBoardMember(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        board_id = request.data.get("board")
        if board_id is None:
            return True  # to allow serializer handle errors

        return Board.objects.filter(
            Q(id=board_id),
            Q(owner=request.user) | Q(members=request.user),
        ).exists()


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user

        return (
            obj.members.filter(pk=request.user.pk).exists() or obj.owner == request.user
        )


class IsTaskCreatorOrBoardOwnerOrBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # DELETE: only task.creator or board.owner
        if request.method == "DELETE":
            return obj.created_by == user or obj.board.owner == user

        # any board member or owner can view/update:
        return obj.board.owner == user or obj.board.members.filter(pk=user.pk).exists()
