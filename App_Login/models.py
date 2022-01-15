from django.db import models

# To Create A Custom User Model and admin panel
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.


class MyuserManager(
    BaseUserManager
):  # To Manage new users using this baseusermanaegr class
    """ A Custom User Manager to deal with Emails  as an unique Identifier """

    def _create_user(self, email, password, **extra_fields):
        """Creates and Saves an user with given email and password """

        if not email:
            raise ValueError("Email Must Be Set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("SuperUser is_staff must be True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("SuperUser is_superuser must be True")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_staff = models.BooleanField(
        gettext_lazy("staff_status"),
        default=False,
        help_text="Determines Whether They Can Log in this Site or not",
    )
    is_active = models.BooleanField(
        gettext_lazy("active"),
        default=True,
        help_text="Determines Whether their Account Status is Active or not",
    )
    USERNAME_FIELD = "email"
    objects = MyuserManager()

    class Meta:
        verbose_name_plural = "User"
        db_table = "User"

    def __str__(self):
        return self.email


def upload_image(instance, filename):
    return "profile/{instance.user.email}/{instance.user.email}profile_pic.png".format(
        instance=instance
    )


class UserProfile(models.Model):
    first_name = models.CharField(max_length=264, blank=True)
    last_name = models.CharField(max_length=264, blank=True)
    username = models.CharField(max_length=264, blank=True)
    profile_pic = models.ImageField(
        upload_to=upload_image, blank=True, default="/profile/default.png"
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userprofile",
    )

    class Meta:
        verbose_name_plural = "User Profile"
        db_table = "User Profile"

    def __str__(self):
        return self.user.email + " 's Profile"


class Plans(models.Model):
    plan_name = models.CharField(max_length=260)
    amount = models.FloatField()
    plan_id = models.CharField(max_length=260, unique=True)
    plan_description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Plans"
        db_table = "Plans"

    def __str__(self):
        return self.plan_name


class UserPlans(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="userprofileplan",
    )
    plan = models.OneToOneField(Plans, on_delete=models.SET_NULL, null=True)
    paid = models.BooleanField(default=False)
    billing_address = models.TextField(blank=True)
    billing_email = models.EmailField(blank=True)

    class Meta:
        verbose_name_plural = "User Plans"
        db_table = "User Plans"

    def __str__(self):
        return self.user.user.email + " 's Plan"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    instance.userprofile.save()
