# to be able to work only with User i do not need anything
# just User = get_user_model() , where i neeed User

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    fullname = models.CharField(max_length=255, blank=True)
    # add other fields here


# next variant

# from django.contrib.auth.models import User
# from django.db import models


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     fullname = models.CharField(max_length=150)

#     def __str__(self):
#         return self.fullname
