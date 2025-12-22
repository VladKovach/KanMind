from django.urls import path

from kanmind_app.api.views import (
    BoardDetailView,
    BoardListCreateView,
    EmailCheckView,
    LoginView,
    RegistrationView,
    TaskDetailView,
    TaskListCreateView,
    UsersList,
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UsersList.as_view(), name="users-list"),
    path("boards/", BoardListCreateView.as_view(), name="boards-list"),
    path("boards/<int:pk>", BoardDetailView.as_view(), name="boards-list"),
    path("tasks/", TaskListCreateView.as_view(), name="tasks-list"),
    path("tasks/<int:pk>", TaskDetailView.as_view(), name="tasks-detail"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    # path("boards/"),
    # path("boards/<int:pk>/"),
    # path("tasks/"),
    # path("tasks/<int:pk>/"),
    # path("tasks/reviewing/"),
    # path("tasks/assigned-to-me/"),
    # path("tasks/<int:pk>/comments/"),
    # path("tasks/<int:pk>/comments/<int:pk>/"),
]
