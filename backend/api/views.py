from django.http import FileResponse
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribers, User

from .filters import IngredientsFilter, RecipesFilter
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (AddRecipeSerializer, FavoriteRecipesSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionsListSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели Пользователя."""

    def get_queryset(self):
        """Лимитирование кол-ва отображаемых пользователей в ответе."""
        limit = self.request.query_params.get('limit')
        if limit:
            return User.objects.all()[:int(limit)]
        return User.objects.all()

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Получить доступ к своей странице по адресу /users/me/
           может только авторизированный пользователь."""
        self.get_object = self.get_instance
        return self.retrieve(request)

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращает список авторов рецептов, на которых подписан текущий
           пользователь. В выдачу добавляются рецепты авторов и их кол-во."""
        limit = self.request.query_params.get('limit')
        if limit:
            subscriptions = Subscribers.objects.filter(
                user=request.user)[:int(limit)]
        else:
            subscriptions = Subscribers.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsListSerializer(pages,
                                                 many=True,
                                                 context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/subscribe')
    def subscribe(self, request, id):
        """Подписаться или отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(data={'author': author.id,
                                                   'user': request.user.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscription = get_object_or_404(Subscribers,
                                             author=author.id,
                                             user=request.user.id)
            serializer = SubscriptionsListSerializer(
                subscription,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscribers.objects.filter(author=author.id,
                                                      user=request.user.id)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': "Вы не подписаны на этого автора!"},
                            status=status.HTTP_400_BAD_REQUEST)


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get', ]


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
    http_method_names = ['get', ]


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filterset_class = RecipesFilter

    def get_queryset(self):
        """Лимитирование кол-ва отображаемых рецептов в ответе."""
        limit = self.request.query_params.get('limit')
        if limit:
            return Recipe.objects.all()[:int(limit)]
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return AddRecipeSerializer

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Формат файла: file.txt"""
        shoppingcart = ShoppingCart.objects.filter(user=request.user)
        recipeingredients = (RecipeIngredient.objects.filter(
            recipe=i['recipe_id']).values() for i in shoppingcart.values())
        ingredients = {}
        for recipeingredient in recipeingredients:
            for i in recipeingredient:
                ingredient = Ingredient.objects.get(id=i['ingredients_id'])
                amount = i['amount']
                if ingredient.name not in ingredients:
                    ingredients[ingredient.name] = (
                        ingredient.measurement_unit,
                        amount)
                else:
                    ingredients[ingredient.name] = (
                        ingredient.measurement_unit,
                        ingredients[ingredient.name][1] + amount)
        with open("shopping_cart.txt", "w") as file:
            file.write('Ваш список покупок:' + '\n')
            for ingredient, amount in sorted(ingredients.items(),
                                             key=lambda x: x[0]):
                file.write(f'{ingredient} - {amount[1]}({amount[0]}).' + '\n')
            file.close()
        return FileResponse(open('shopping_cart.txt', 'rb'))

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/shopping_cart')
    def shopping_cart(self, request, id):
        """Добавление или удаление рецепта в список покупок."""
        if request.method == 'POST':
            if not Recipe.objects.filter(id=id).exists():
                return Response({'errors': 'Рецепт не найден!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=id)
            shoppingcart_status = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe).exists()
            if shoppingcart_status:
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=id)
            shoppingcart_status = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe).exists()
            if shoppingcart_status:
                ShoppingCart.objects.get(user=request.user,
                                         recipe=recipe).delete()
                return Response('Рецепт удалён из списка покупок!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/favorite')
    def favorite(self, request, id):
        """Добавление или удаление рецепта в избранное."""
        if request.method == 'POST':
            if not Recipe.objects.filter(id=id).exists():
                return Response({'errors': 'Рецепт не найден!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=id)
            shoppingcart_status = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe).exists()
            if shoppingcart_status:
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteRecipesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=id)
            shoppingcart_status = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe).exists()
            if shoppingcart_status:
                FavoriteRecipes.objects.get(user=request.user,
                                            recipe=recipe).delete()
                return Response('Рецепт удалён из избранного!',
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)
