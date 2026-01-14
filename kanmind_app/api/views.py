from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanmind_app.api.permissions import (
    IsBoardMemberForTaskComments,
    IsBoardMemberForTasks,
    IsBoardOwnerOrMember,
    IsCommentAuthor,
    IsTaskCreatorOrBoardOwnerOrBoardMember,
)
from kanmind_app.models import Board, Comment, Task

from .serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    CommentSerializer,
    EmailFilterSerializer,
    LoginSerializer,
    RegistrationSerializer,
    TaskDetailSerializer,
    TaskSerializer,
    UserSerializer,
)

User = get_user_model()


class RegistrationView(APIView):
    """Handles user registration with token authentication.

    Accepts email, password, fullname. Creates user + token in single transaction.
    Returns user data + token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create or get existing token for user
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "fullname": user.fullname,
                    "email": user.email,
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Authenticates user credentials and returns token + user data."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "fullname": user.fullname,
                    "email": user.email,
                    "user_id": user.id,
                }
            )
        return Response(serializer.errors, status=400)


class BoardListCreateView(ListCreateAPIView):
    """CRUD operations for Boards - List user's boards + create new ones.

    GET: Returns boards where user is owner OR member
    POST: Creates board with current user as owner
    """

    serializer_class = BoardListSerializer

    def get_queryset(self):
        """Filter boards to only show user's owned or member boards."""

        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """Automatically set board owner to current user."""
        serializer.save(owner=self.request.user)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """Detailed board operations with ownership/member permissions.

    Requires: IsAuthenticated + IsBoardOwnerOrMember permission
    URL: /boards/{board_id}/
    """

    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardOwnerOrMember]
    lookup_url_kwarg = "board_id"


class TaskListCreateView(ListCreateAPIView):
    """Task creation within boards + list all tasks.

    Permissions: IsAuthenticated + IsBoardMemberForTasks (board access check)
    POST requires 'board' ID in request body
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTasks]

    def perform_create(self, serializer):
        """Set task creator to current authenticated user."""
        serializer.save(created_by=self.request.user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """Individual task operations with granular permissions.

    DELETE: Only task creator OR board owner
    GET/PATCH: Board members/owners
    URL: /tasks/{task_id}/
    """

    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [
        IsAuthenticated,
        IsTaskCreatorOrBoardOwnerOrBoardMember,
    ]
    lookup_url_kwarg = "task_id"


class EmailCheckView(ListAPIView):
    """Check if email exists.

    GET: /email-check/?email=example@test.com
    Returns 404 if email not found
    """

    serializer_class = UserSerializer

    def get_queryset(self):
        """Validate query params + filter users by email (case-insensitive)."""

        filter_serializer = EmailFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)

        email = filter_serializer.validated_data["email"]
        return User.objects.filter(email__iexact=email)

    def list(self, request, *args, **kwargs):
        """Override list to return single user or 404."""

        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            raise NotFound("Email nicht gefunden. Die Email existiert nicht.")

        # Serialize the single user
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class AssignedToUserTasksView(ListAPIView):
    """List all tasks assigned to current user."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class UserIsReviewingTasksView(ListAPIView):
    """List all tasks where current user is reviewer."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


class CommentsListCreateView(ListCreateAPIView):
    """Task comments - list + create.

    URL: /tasks/{task_id}/comments/
    Permissions check board membership via task relationship
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskComments]

    def get_queryset(self):
        """Filter comments by task_id from URL kwargs."""
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        """Set comment author + parent task id."""
        task_id = self.kwargs["task_id"]
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentsDetailView(DestroyAPIView):
    """Delete individual comments.

    Only comment author can delete
    URL: /tasks/{task_id}/comments/{comment_id}/
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated, IsCommentAuthor]
