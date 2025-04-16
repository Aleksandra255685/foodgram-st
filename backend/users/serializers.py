from rest_framework import serializers
from .models import User, Subscription
from core.fields import Base64ImageField
from djoser.serializers import UserSerializer


class CustomUserSerializer(UserSerializer):
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed',
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        from recipes.serializers import RecipeShortSerializer
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
