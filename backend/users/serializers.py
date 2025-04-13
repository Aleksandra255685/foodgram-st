from rest_framework import serializers

from api.serializers import UserProfileSerializer
from recipes.serializers import ShortRecipeSerializer
from .models import Subscription


class SubscriptionSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.ReadOnlyField(source="recipes.count")

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get("recipes_limit")

        if recipes_limit and recipes_limit.isdigit():
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return ShortRecipeSerializer(
            recipes, context={"request": request}, many=True
        ).data


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "author",
            "subscriber",
        )

    def validate(self, data):
        if data["subscriber"] == data["author"]:
            raise serializers.ValidationError(
                "Вы пытаетесь подписаться на себя!"
            )

        return data
