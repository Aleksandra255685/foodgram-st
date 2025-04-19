from django.db.models import Sum
from django.http import FileResponse
from io import BytesIO
from backend.recipes.models import RecipeIngredient


def get_shopping_list_ingredients(user):
    return (
        RecipeIngredient.objects
        .filter(recipe__shopping_carts__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_amount=Sum('amount'))
        .order_by('ingredient__name')
    )


def render_shopping_list_text(ingredients):
    return '\n'.join(
        f'{item["ingredient__name"]} — {item["total_amount"]} {item["ingredient__measurement_unit"]}'
        for item in ingredients
    )


def generate_shopping_list_file(user):
    ingredients = get_shopping_list_ingredients(user)
    content = render_shopping_list_text(ingredients)

    buffer = BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shopping_list.txt',
        content_type='text/plain'
    )
