import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'email', 'username', 'bio',
            'role', 'first_name', 'last_name',
        ]
        model = User
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email', 'username']
        model = User
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError(f'Никнеим: {username} недоступен')
        return username


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'pub_date',)
        model = Review

    def only_one_review(self, request, *args, **kwargs):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        if Review.objects.filter(
            author=self.request.user,
            title=title
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Category
        extra_kwargs = {
            'name': {'required': False},
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug',)
        model = Genre
        extra_kwargs = {
            'name': {'required': False},
        }


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'description', 'category',
                  'rating')


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True, read_only=False,
                                         queryset=Genre.objects.all(),
                                         slug_field='slug')
    category = serializers.SlugRelatedField(many=False, read_only=False,
                                            queryset=Category.objects.all(),
                                            slug_field='slug')

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise ValidationError('Указан некорректный год!')
        return value
