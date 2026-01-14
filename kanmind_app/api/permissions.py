from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanmind_app.models import Board, Task


class IsBoardOwnerOrMember(BasePermission):
    """Object-level permission for Board detail operations.

    DELETE: Only board owner
    GET/PATCH/PUT: Board owner OR member
    """

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user

        # Read/update: owner or member can access
        return (
            obj.members.filter(pk=request.user.pk).exists()
            or obj.owner == request.user
        )


class IsBoardMemberForTasks(BasePermission):
    """Permission for TaskListCreateView - validates task access on CREATE.

    SAFE_METHODS (GET): allowed
    POST: User must be board owner/member
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        board_id = request.data.get("board")
        get_object_or_404(
            Board, id=board_id
        )  # 404 if no board found, continiue otherwise

        if board_id is None:
            return True  # Let serializer validate required field

        try:
            board_id = int(board_id)
            return Board.objects.filter(
                Q(id=board_id),
                Q(owner=request.user) | Q(members=request.user),
            ).exists()
        except (ValueError, TypeError):
            return True  # Let serializer return 400 Bad Request


class IsTaskCreatorOrBoardOwnerOrBoardMember(BasePermission):
    """Permissions for individual task operations.

    DELETE: Task creator OR board owner only
    GET/PATCH/PUT: Any board member/owner
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method == "DELETE":
            return obj.created_by == user or obj.board.owner == user

        # Read/update: Any board member/owner
        return (
            obj.board.owner == user
            or obj.board.members.filter(pk=user.pk).exists()
        )


class IsBoardMemberForTaskComments(BasePermission):
    """Permission for task comments endpoints.

    Validates user has access to task's parent board.
    URL pattern: /tasks/{task_id}/comments/
    """

    def has_permission(self, request, view):
        task_id = view.kwargs.get("task_id")
        get_object_or_404(
            Task, id=task_id
        )  # 404 if no task found, continiue otherwise

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False

        board = task.board
        # User must be board owner or member to create comment
        return (
            board.owner == request.user
            or board.members.filter(pk=request.user.pk).exists()
        )


class IsCommentAuthor(BasePermission):
    """Restricts comment deletion to author only."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
