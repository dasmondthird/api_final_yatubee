from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

from posts.models import Post, Group, User, Follow
from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer,
)
from .permissions import IsAuthorOrReadOnly

# Настройка логгера
logger = logging.getLogger(__name__)


@extend_schema(
    responses={
        200: PostSerializer,
        404: OpenApiResponse(
            description='Empty response, post by id not found'),
    }
)
class FollowViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """Список подписок."""

    serializer_class = FollowSerializer
    filter_backends = [SearchFilter]
    search_fields = ['following__username']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating follow: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={
        200: PostSerializer,
        404: OpenApiResponse(
            description='Empty response, post by id not found'),
    }
)
class PostViewSet(viewsets.ModelViewSet):
    """Список постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(
    responses={
        200: GroupSerializer,
        404: OpenApiResponse(
            description='Empty response, post by id not found'),
    }
)
class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Список групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@extend_schema(
    responses={
        200: CommentSerializer,
        404: OpenApiResponse(
            description='Empty response, post by id not found'),
    }
)
class CommentViewSet(viewsets.ModelViewSet):
    """Список комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly]

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(author=self.request.user, post=post)
