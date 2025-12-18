from django.urls import path

from kanmind_app.api.views import LoginView, RegistrationView, UsersList

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UsersList.as_view(), name="users-list"),
    # path("boards/"),
    # path("boards/<int:pk>/"),
    # path("email-check/"),
    # path("tasks/"),
    # path("tasks/<int:pk>/"),
    # path("tasks/reviewing/"),
    # path("tasks/assigned-to-me/"),
    # path("tasks/<int:pk>/comments/"),
    # path("tasks/<int:pk>/comments/<int:pk>/"),
]
