from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.shortcuts import get_object_or_404

from posts.models import Post, Group, Comment, User, Follow


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    following = serializers.SlugRelatedField(
        slug_field='username', 
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Подписка на автора оформлена ранее!',
            )
        ]

    def validate_following(self, value):
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        following = validated_data['following']
        follow = Follow.objects.create(user=user, following=following)
        return follow

    def to_representation(self, instance):
        return {
            'user': instance.user.username,
            'following': instance.following.username,
        }


class PostSerializer(serializers.ModelSerializer):
    """Сериализация постов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Post
        fields = ('id', 'text', 'author', 'pub_date', 'group', 'image')


class GroupSerializer(serializers.ModelSerializer):
    """Сериализация групп."""

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализация комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'post', 'created')
        read_only_fields = ('post',)
