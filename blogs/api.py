# -*- coding: utf-8 -*-
from blogs.filters import PostFilter
from blogs.models import Blog, Post
from blogs.permissions import PostPermissions
from blogs.serializers import BlogSerializer, BlogPostsSerializer, PostSerializer, PostListSerializer
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter, DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class BlogsViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Blog.objects.select_related('owner').annotate(posts_count=Count('posts')).all().order_by('name')
    serializer_class = BlogSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'description', 'owner__username')
    ordering_fields = ('name', 'owner', 'created_at')

    def get_serializer_class(self):
        """
        Returns a different serializer when action is retrieve
        """
        return self.serializer_class if self.action != 'retrieve' else BlogPostsSerializer


class PostsViewSet(ModelViewSet):
    queryset = Post.objects.select_related('blog__owner').all().order_by('-publish_date')
    serializer_class = PostSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class = PostFilter
    search_fields = ('title', 'intro', 'body')
    ordering_fields = ('title', 'publish_date')
    permission_classes = (IsAuthenticatedOrReadOnly, PostPermissions)

    def get_serializer_class(self):
        """
        Returns a different serializer when action is list
        """
        return self.serializer_class if self.action != 'list' else PostListSerializer

    def get_queryset(self):
        """
        If user is not authenticated, returns only published posts
        If user is authenticated and not superuser, returns all its posts and published posts from others
        If user is superuser, returns all posts
        """
        if self.action == 'retrieve':  # retrieves blog's info in the same db query
            self.queryset.select_related('blog')

        # if not authenticated, returns only published posts
        if not self.request.user.is_authenticated():
            return self.queryset.filter(publish_date__lte=timezone.now())

        # if is superuser, returns all
        elif self.request.user.is_superuser:
            return self.queryset

        # if is not superuser, returns their own posts and others published
        else:
            return self.queryset.filter(
                Q(blog=self.request.user.blog) | Q(publish_date__lte=timezone.now())
            )

    def perform_create(self, serializer):
        """
        Force the post's blog to be the auth user's blog
        """
        serializer.save(blog=self.request.user.blog)
        return serializer
