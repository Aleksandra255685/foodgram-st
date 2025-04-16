from django.contrib import admin
from django.urls import path, include
from api.views import RecipeViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path("s/<int:pk>", RecipeViewSet.as_view({"get": "retrieve"})),
]
