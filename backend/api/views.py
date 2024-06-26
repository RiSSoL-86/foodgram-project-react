from django.db.models import F
from django.http import FileResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribers, User
from .filters import IngredientsFilter, RecipesFilter
from .paginations import Pagination
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (AddRecipeSerializer, FavoriteRecipesSerializer,
                          GetRecipeSerializer, IngredientSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionsListSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели Пользователя."""
    pagination_class = Pagination

    def get_permissions(self):
        """Настройка разрешений."""
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated, ]
        return super(UserViewSet, self).get_permissions()

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        """Возвращает список авторов рецептов, на которых подписан текущий
           пользователь. В выдачу добавляются рецепты авторов и их кол-во."""
        subscriptions = Subscribers.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsListSerializer(pages,
                                                 many=True,
                                                 context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=[IsAuthenticated, ],
            url_path=r'(?P<id>\d+)/subscribe')
    def subscribe(self, request, id):
        """Подписаться или отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        data = {'author': author.id,
                'user': request.user.id}
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription, _ = Subscribers.objects.filter(
                author=author.id,
                user=request.user.id).delete()
            if subscription:
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
    pagination_class = Pagination
    permission_classes = (IsAuthorAdminOrReadOnly,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return AddRecipeSerializer

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Формат файла: file.txt"""
        shoppingcart = ShoppingCart.objects.filter(
            user=request.user).values('recipe_id__ingredients__name').annotate(
                amount=F('recipe_id__recipeingredients__amount'),
                measurement_unit=F('recipe_id__ingredients__measurement_unit')
        ).order_by('recipe_id__ingredients__name')
        ingredients = {}
        for ingredient in shoppingcart:
            ingredient_name = ingredient['recipe_id__ingredients__name']
            amount = ingredient['amount']
            measurement_unit = ingredient['measurement_unit']
            if ingredient_name not in ingredients:
                ingredients[ingredient_name] = (amount, measurement_unit)
            else:
                ingredients[ingredient_name] = (
                    ingredients[ingredient_name][0] + amount,
                    measurement_unit)
        with open("shopping_cart.txt", "w") as file:
            file.write('Ваш список покупок:' + '\n')
            for ingredient, amount in ingredients.items():
                file.write(f'{ingredient} - {amount[0]}({amount[1]}).' + '\n')
            file.close()
        return FileResponse(open('shopping_cart.txt', 'rb'))

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=[IsAuthenticated, ],
            url_path=r'(?P<id>\d+)/shopping_cart')
    def shopping_cart(self, request, id):
        """Добавление или удаление рецепта в список покупок."""
        if request.method == 'POST':
            if not Recipe.objects.filter(id=id):
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
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=id)
            if not Recipe.objects.filter(id=id):
                return Response({'errors': 'Рецепт не найден!'},
                                status=status.HTTP_400_BAD_REQUEST)
            shoppingcart_status, _ = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe).delete()
            if shoppingcart_status:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=False,
            permission_classes=[IsAuthenticated, ],
            url_path=r'(?P<id>\d+)/favorite')
    def favorite(self, request, id):
        """Добавление или удаление рецепта в избранное."""
        if request.method == 'POST':
            if not Recipe.objects.filter(id=id):
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
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=id)
            if not Recipe.objects.filter(id=id):
                return Response({'errors': 'Рецепт не найден!'},
                                status=status.HTTP_400_BAD_REQUEST)
            shoppingcart_status, _ = FavoriteRecipes.objects.filter(
                user=request.user,
                recipe=recipe).delete()
            if shoppingcart_status:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт не найден в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
