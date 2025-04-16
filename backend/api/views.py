from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from users.models import User, Subscription
from users.serializers import (CustomUserSerializer,
                               SubscriptionSerializer, AvatarSerializer)

from recipes.models import (Recipe, Ingredient,
                            Favorite, ShoppingCart, RecipeIngredient)
from recipes.serializers import (RecipeSerializer,
                                 IngredientSerializer,
                                 RecipeShortSerializer)

from core.permissions import IsAuthorOrReadOnly
from core.utils import generate_shopping_list_file
from core.filters import RecipeFilter


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
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filterset_fields = ['author', 'is_favorited', 'is_in_shopping_cart']
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated], url_path='favorite')
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'error': 'Уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = Favorite.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не найден в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated], url_path='shopping_cart')
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'error': 'Уже в писке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(
                user=user, recipe=recipe).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепт не найден в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return generate_shopping_list_file(request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()

        url = f"{request.get_host()}/s/{recipe.pk}"

        return Response(data={"short-link": url})


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated], url_path='subscribe')
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        user = request.user

        if request.method == 'POST':
            if author == user:
                return Response({'error': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'error': 'Уже подписан'},
                                status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(author,
                                                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(
                user=user, author=author).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Подписка не найдена'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated],
            url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [sub.author for sub in subscriptions]

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            authors, many=True,
            context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
