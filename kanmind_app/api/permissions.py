from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanmind_app.models import Board, Task


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user

        return (
            obj.members.filter(pk=request.user.pk).exists()
            or obj.owner == request.user
        )


class IsBoardMemberForTasks(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        board_id = request.data.get("board")
        get_object_or_404(Board, id=board_id)

        if board_id is None:
            return True  # to allow serializer handle errors
        try:
            board_id = int(board_id)
            return Board.objects.filter(
                Q(id=board_id), Q(owner=request.user) | Q(members=request.user)
            ).exists()
        except (ValueError, TypeError):
            return True


class IsTaskCreatorOrBoardOwnerOrBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # DELETE: only task.creator or board.owner
        if request.method == "DELETE":
            return obj.created_by == user or obj.board.owner == user

        # any board member or owner can view/update:
        return (
            obj.board.owner == user
            or obj.board.members.filter(pk=user.pk).exists()
        )


class IsBoardMemberForTaskComments(BasePermission):

    def has_permission(self, request, view):
        task_id = view.kwargs.get("task_id")
        get_object_or_404(Task, id=task_id)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False

        board = task.board
        return (
            board.owner == request.user
            or board.members.filter(pk=request.user.pk).exists()
        )


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.author == request.user
