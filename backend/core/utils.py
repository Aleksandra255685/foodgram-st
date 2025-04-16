from django.http import HttpResponse
from recipes.models import RecipeIngredient


def generate_shopping_list_file(user):
    ingredients = {}
    recipes = user.shopping_cart.values_list('recipe', flat=True)
    recipe_ingredients = RecipeIngredient.objects.filter(recipe__in=recipes)

    for item in recipe_ingredients:
        name = item.ingredient.name
        unit = item.ingredient.measurement_unit
        amount = item.amount

        if name not in ingredients:
            ingredients[name] = {'amount': 0, 'unit': unit}
        ingredients[name]['amount'] += amount

    lines = [f'{name} — {data["amount"]} {data["unit"]}'
             for name, data in ingredients.items()]
    content = '\n'.join(lines)

    return HttpResponse(content, content_type='text/plain', headers={
        'Content-Disposition': 'attachment; filename="shopping_list.txt"'
    })
