from django.db import models, migrations
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django_extensions.db.fields import RandomCharField
from .utils import generate_code

class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not first_name:
            raise ValueError("Users must enter their first name")
        if not last_name:
            raise ValueError("Users must enter their last name")

        user = self.model(
               email      = self.normalize_email(email),
               first_name = first_name,
               last_name  = last_name,
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):

        user = self.create_user(
               email      = self.normalize_email(email),
               first_name = first_name,
               last_name  = last_name,
               password   = password,
            )

        user.is_admin     = True
        user.is_staff     = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class Team(models.Model):
    Name    = models.CharField(max_length=60)
    code    = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.Name

    def save(self, *args, **kwargs):
        if self.code == "":
            code = generate_code()
            self.code = code
        super().save(*args, **kwargs)
        
class User(AbstractBaseUser, PermissionsMixin):

    USER_CHOICES = [
        ('CO', 'Coach'),
        ('PL', 'Parent'),
        ('PA', 'Player'),
        ]

    email        = models.EmailField(verbose_name='email', max_length=60, unique=True)
    date_joined  = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    is_active    = models.BooleanField(default=True)   ## Everything within these comment tags
    is_admin     = models.BooleanField(default=False)  ## define the permissions
    is_staff     = models.BooleanField(default=False)  ## that the user will have unless
    is_superuser = models.BooleanField(default=False)  ## changed by the superuser/admin.
    is_parent    = models.BooleanField(default=False)
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50)
    uuid1        = models.UUIDField(default=uuid.uuid4, primary_key=True)
    team         = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL) # Set to null when assigned team is deleted
    user_type    = models.CharField(choices=USER_CHOICES, default='CO', max_length=20)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + " " + self.last_name # Returns the email, first name and
                                                      # last name of the user.

    def has_perm(self, perm, obj=None): # Assigns the permissions that the user has
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Video(models.Model):
    Name       = models.CharField(max_length=60)
    Video      = models.FileField(upload_to='videos/')
    team       = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Fixture(models.Model):
    Name           = models.CharField(max_length=100, blank=True)
    team1          = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team1")
    team2          = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team2")
    address_1      = models.CharField(max_length=100, null=True)
    address_2      = models.CharField(max_length=100, null=True, blank=True)
    city           = models.CharField(max_length=50, null=True)
    zip_code       = models.CharField(max_length=10, null=True)
    date           = models.DateTimeField(null=True)

    def __str__(self):
        return self.Name