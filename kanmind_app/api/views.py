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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(
                user=user
            )  # optional: token auth
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


# Boards
class BoardListCreateView(ListCreateAPIView):
    serializer_class = BoardListSerializer

    def get_queryset(self):
        user = self.request.user

        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsBoardOwnerOrMember]
    lookup_url_kwarg = "board_id"


# Tasks


class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTasks]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsTaskCreatorOrBoardOwnerOrBoardMember]
    lookup_url_kwarg = "task_id"


# Email Check
class EmailCheckView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        # Validate ALL query params at once
        filter_serializer = EmailFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)

        email = filter_serializer.validated_data["email"]
        return User.objects.filter(email__iexact=email)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 404 if no user found
        if not queryset.exists():
            raise NotFound("Email nicht gefunden. Die Email existiert nicht.")

        # Serialize the single user
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)


class AssignedToUserTasksView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class UserIsReviewingTasksView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)


# Comments


class CommentsListCreateView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTaskComments]

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs["task_id"]
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentsDetailView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_url_kwarg = "comment_id"
    permission_classes = [IsAuthenticated, IsCommentAuthor]
