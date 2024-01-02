from django.db import models
from django.contrib.auth.models import AbstractUser

NUll_AND_BLANK = {"null": True, "blank": True}


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('mod', 'Moderator'),
        ('user', 'Regular User'),
    ]
    is_email_verified = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='user'  # You can set a default value if needed
    )

    def __str__(self):
        return f'{self.email}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    address = models.TextField(**NUll_AND_BLANK)
    image = models.ImageField(upload_to="img", **NUll_AND_BLANK)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profile"
        ordering = ["-id"]

    def __str__(self):
        return self.user.username


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField(upload_to="product", **NUll_AND_BLANK)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-id"]

    def __str__(self):
        return self.title
