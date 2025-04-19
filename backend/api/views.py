from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.filters import RecipeFilter
from backend.api.permissions import IsAuthorOrReadOnly
from backend.api.serializers import (RecipeReadSerializer,
                                     RecipeWriteSerializer,
                                     IngredientSerializer,
                                     CustomUserSerializer,
                                     SubscriptionSerializer,
                                     SubscriptionCreateSerializer,
                                     AvatarSerializer,
                                     FavoriteSerializer,
                                     ShoppingCartSerializer
                                     )
from backend.api.utils import generate_shopping_list_file
from backend.recipes.models import (Recipe, Ingredient,
                                    Favorite, ShoppingCart)
from users.models import User, Subscription


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted_count, _ = model.objects.filter(user=request.user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не найден в списке.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='favorite')
    def add_favorite(self, request, pk):
        return self._add_to(request, pk, FavoriteSerializer)

    @add_favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self._remove_from(request, pk, Favorite)

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_shopping_cart(self, request, pk):
        return self._add_to(request, pk, ShoppingCartSerializer)

    @add_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self._remove_from(request, pk, ShoppingCart)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return generate_shopping_list_file(request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        path = reverse('recipes:recipe_short_link', kwargs={'pk': pk})
        url = request.build_absolute_uri(path)
        return Response(data={"short-link": url})


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def _subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _unsubscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        deleted_count, _ = Subscription.objects.filter(user=request.user,
                                                   author=author).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Подписка не найдена.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated], url_path='subscribe')
    def subscribe(self, request, id=None):
        return self._subscribe(request, id)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        return self._unsubscribe(request, id)

    @action(detail=False, permission_classes=[IsAuthenticated],
            url_path='subscriptions')
    def subscriptions(self, request):
        authors = User.objects.filter(subscriptions__user=request.user)

        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
                page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=[IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
