from django.urls import path

from kanmind_app.api.views import (
    AssignedToUserTasksView,
    BoardDetailView,
    BoardListCreateView,
    CommentsDetailView,
    CommentsListCreateView,
    EmailCheckView,
    LoginView,
    RegistrationView,
    TaskDetailView,
    TaskListCreateView,
    UserIsReviewingTasksView,
    UsersList,
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("users/", UsersList.as_view(), name="users-list"),
    path("boards/", BoardListCreateView.as_view(), name="boards-list"),
    path(
        "boards/<int:board_id>/", BoardDetailView.as_view(), name="boards-list"
    ),
    path("tasks/", TaskListCreateView.as_view(), name="tasks-list"),
    path(
        "tasks/<int:task_id>/", TaskDetailView.as_view(), name="tasks-detail"
    ),
    path(
        "tasks/assigned-to-me/",
        AssignedToUserTasksView.as_view(),
        name="assigned-to-user",
    ),
    path(
        "tasks/reviewing/",
        UserIsReviewingTasksView.as_view(),
        name="user-reviewing",
    ),
    path(
        "tasks/<int:task_id>/comments/",
        CommentsListCreateView.as_view(),
        name="comments-list",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        CommentsDetailView.as_view(),
        name="comments-detail",
    ),
]
