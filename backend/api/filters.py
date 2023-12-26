from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientsFilter(SearchFilter):
    """Кастомная настройка фильтра для Ингридиентов."""
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    """Кастомная настройка фильтра для Рецептов."""
    author = filters.CharFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует избранные рецепты пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(favoriterecipes__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты в списке рецептов пользователя."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
