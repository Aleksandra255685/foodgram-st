from django_filters import rest_framework

from .models import Recipe


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.filters.BooleanFilter(
        method="is_recipe_in_favorites_filter"
    )
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method="is_recipe_in_shoppingcart_filter"
    )

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_recipe_in_shoppingcart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_carts__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")
