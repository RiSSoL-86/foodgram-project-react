from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscribers, User

DEFAULT_RECIPES_LIMIT = 6


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора рецепта."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribers.objects.filter(author=obj,
                                          user=user).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class HelperRecipeSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для корректного отображения рецептов
       в списке рецептов автора."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок для текущего
       пользователя."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribers
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на автора рецепта."""
        user = self.context.get('request').user
        return Subscribers.objects.filter(author=obj.author,
                                          user=user).exists()

    def get_recipes(self, obj):
        """Список рецептов автора."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', DEFAULT_RECIPES_LIMIT)
        return HelperRecipeSerializer(
            Recipe.objects.filter(author=obj.author)[:int(limit)],
            many=True
        ).data

    def get_recipes_count(self, obj):
        """Кол-во рецептов автора."""
        return Recipe.objects.filter(author=obj.author).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели подписок."""

    def validate(self, data):
        """Валидация на подписку."""
        if data['author'] == data['user']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        if Subscribers.objects.filter(author=data['author'],
                                      user=data['user']).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора!')
        return data

    class Meta:
        model = Subscribers
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для Тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetRecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный cериалайзер для корректного отображения
       Ингредиентов - рецепта."""
    id = serializers.ReadOnlyField(
        source='ingredients.id')
    name = serializers.ReadOnlyField(
        source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Cериалайзер для метода GET модели рецептов."""
    author = UsersSerializer(read_only=True)
    ingredients = GetRecipeIngredientSerializer(many=True,
                                                source='recipeingredients',
                                                read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        """Являяется ли рецепт избранным для текущего пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(recipe=obj,
                                              user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Является ли рецепт в списке покупок для текущего пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=user).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class AddRecipeIngredientSerializer(serializers.ModelSerializer):
    """Вспомогательный cериалайзер для корректного добавления
       Ингредиентов в рецепт при его создании."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Cериалайзер для метода Post, PATCH и DEL модели рецептов."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True,
                                              write_only=True)
    ingredients = AddRecipeIngredientSerializer(many=True, write_only=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField()

    def add_tags(self, tags, recipe):
        """Сохранение в БД тэгов рецепта."""
        recipe.tags.set(tags)

    def add_ingredients(self, ingredients, recipe):
        """Сохранение в БД ингридиентов рецепта."""
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount'])

    def validate(self, data):
        """Валидация при создании рецепта."""
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        image = data.get('image')
        if not ingredients:
            raise serializers.ValidationError('Укажите необходимые ингридиенты'
                                              ' для рецепта!')
        if not tags:
            raise serializers.ValidationError('Укажите тэг для рецепта!')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Вы указали одинаковые теги при '
                                              'создании рецепта!')
        ingredients_id_list = [id['id'] for id in ingredients]
        if len(ingredients_id_list) != len(set(ingredients_id_list)):
            raise serializers.ValidationError('Вы указали одинаковые '
                                              'ингридиенты при создании '
                                              'рецепта!')
        ingredients_amount_list = [amount['amount'] for amount in ingredients]
        if (ingredients_amount_list != list(map(abs, ingredients_amount_list))
                or 0 in ingredients_amount_list):
            raise serializers.ValidationError('Укажите значение больше 1!')
        if not image:
            raise serializers.ValidationError('Вы не указали картинку '
                                              'рецепта!')
        return data

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        """Внесение изменений в рецепт."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe = super().update(recipe, validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, recipe):
        """Корректировка отображения информации о созданном рецепте."""
        data = super().to_representation(recipe)
        data['tags'] = recipe.tags.values()
        data['ingredients'] = [{
            'id': Ingredient.objects.get(id=i.get('ingredients_id')).id,
            'name': Ingredient.objects.get(
                id=i.get('ingredients_id')).name,
            'measurement_unit': Ingredient.objects.get(
                id=i.get('ingredients_id')).measurement_unit,
            'amount': i.get('amount')}
            for i in recipe.recipeingredients.values()]
        author = User.objects.get(id=recipe.author.id)
        user = self.context.get('request').user
        data['author'] = {
            'email': author.email,
            'id': author.id,
            'username': author.username,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'is_subscribed': Subscribers.objects.filter(
                author=author,
                user=user).exists()
        }
        return data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Списка покупок."""
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Избранных рецептов."""
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = FavoriteRecipes
        fields = ('id', 'name', 'image', 'cooking_time')
