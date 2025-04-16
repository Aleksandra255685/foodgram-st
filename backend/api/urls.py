from django.urls import include, path
from rest_framework import routers
from .views import RecipeViewSet, IngredientViewSet, UserViewSet

router = routers.DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
