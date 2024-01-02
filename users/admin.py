from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, User, Product
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'is_email_verified', 'user_type')}),
        (('Personal info'), {'fields': ('first_name', 'last_name')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ("username", 'email', 'password', "password2", "is_email_verified", 'user_type')}),
        (('Personal info'), {'fields': ('first_name', 'last_name')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ["id", "username", "is_active", "is_superuser", "is_email_verified", 'user_type']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "address", "display_image"]

    def display_image(self, obj):
        # Assuming your model has an ImageField named 'image_field'
        if obj.image:
            return format_html('<img src="{}" width="100" height="100   " />'.format(obj.image.url))
        else:
            return 'No Image'

    display_image.short_description = 'Image'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "description", "price", "display_image"]

    def display_image(self, obj):
        # Assuming your model has an ImageField named 'image_field'
        if obj.image:
            return format_html('<img src="{}" width="100" height="100   " />'.format(obj.image.url))
        else:
            return 'No Image'
