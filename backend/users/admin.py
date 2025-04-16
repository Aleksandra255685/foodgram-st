from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name')
    list_filter = ("username", "email")
    search_fields = ('email', 'username')
    ordering = ('id',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
