"""
DataBase models
"""
from django.db import models    # type: ignore
from django.contrib.auth.models import (  # type: ignore
    AbstractBaseUser,  # contains the functionality for the authentication system
    BaseUserManager,
    PermissionsMixin  # contains the functionality for the permissions & field system
)

class UserManager(BaseUserManager):
    """Custom user manager"""
    def create_user(self, email, password=None, **extra_fields):
        """Creates, saves and return a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # encrypt the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates , saves and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # define the field used for authentication