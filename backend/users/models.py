from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
   

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        HR = "HR", "HR"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    username = None

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE,
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email