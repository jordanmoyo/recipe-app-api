"""
Test for Recipe API
"""
from decimal import Decimal

from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from rest_framework import status  # type: ignore
from rest_framework.test import APIClient  # type: ignore

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """
    Create and return a sample recipe
    """
    defaults = {
        'title': 'Sample Recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Recipe description',
        'link': 'https://www.example.com/recipe',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """create a sample user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """
    Test unauthenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
    Test authenticated recipe API access
    """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """
        Test retrieving a list of recipes
        """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_list_limited_to_user(self):
        """
        Test retrieving recipes for user
        """
        other_user = create_user(
            email='user2@example.com',
            password='password123'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """
        Test viewing a recipe detail
        """
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """
        Test creating recipe
        """
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """
        Test updating a recipe with patch
        """
        original_link = 'https://www.oringinal_link.com/recipe'
        recipe = create_recipe(
            user=self.user,
            title='sample title',
            time_minutes=25,
            price=Decimal('5.00'),
            link=original_link
        )
        payload = {'title': 'New title'}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe"""
        defaults = {
            'title': 'Sample Recipe title',
            'time_minutes': 22,
            'price': Decimal('5.25'),
            'description': 'Sample Recipe description',
            'link': 'https://www.example.com/recipe',
        }
        payload = {
            'title': 'updated title',
            'time_minutes': 2,
            'price': Decimal('1.25'),
            'description': 'updated Recipe description',
            'link': 'https://www.updated.com/recipe',
        }
        recipe = create_recipe(user=self.user, **defaults)
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(
            user=self.user,
            title='sample recipe',
            time_minutes=3,
            link="https://sample/recipe.com"
        )
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_other_user_error(self):
        """Test trying to delete other users recipe returns an error"""
        other_user = create_user(
            email='other_user@example.com',
            password='pass12345'
        )
        other_user_recipe = create_recipe(user=other_user,)

        url = detail_url(other_user_recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Recipe.objects.filter(id=other_user_recipe.id).exists()
        )
