from rest_framework import serializers
from .models import (
    Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart
)
from core.fields import Base64ImageField
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient_set')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image',
            'text', 'cooking_time', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False

    def validate(self, data):
        ingredients_data = self.initial_data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError({
                'ingredients': 'Нужно добавить хотя бы один ингредиент.'
            })

        ingredient_ids = set()
        for item in ingredients_data:
            ing_id = item.get('id')
            amount = item.get('amount')

            if ing_id in ingredient_ids:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться.'
                })
            ingredient_ids.add(ing_id)

            if int(amount) < 1:
                raise serializers.ValidationError({
                    'ingredients': 'Количество должно быть больше 0.'
                })

        if data.get('cooking_time', 0) < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время готовки должно быть не менее 1 минуты.'
            })

        return data

    def create_ingredients(self, recipe, ingredients_data):
        for item in ingredients_data:
            ingredient = item['ingredient']
            amount = item['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
