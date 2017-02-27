# -*- coding: utf-8 -*-
from collections import OrderedDict
from blogs.models import Blog, Post
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination


class BlogOwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class BlogSerializer(serializers.ModelSerializer):
    owner = BlogOwnerSerializer(read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    posts_count = serializers.ReadOnlyField()

    class Meta:
        model = Blog


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer(read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    author = serializers.CharField(source='get_author', read_only=True)

    class Meta:
        model = Post
        read_only_fields = ('blog',)


class PostListSerializer(PostSerializer):

    class Meta(PostSerializer.Meta):
        fields = ('id', 'title', 'intro', 'image_url', 'url', 'author')


class BlogPostListSerializer(PostSerializer):

    class Meta(PostSerializer.Meta):
        fields = ('id', 'title', 'intro', 'image_url', 'url')


class BlogPostsSerializer(BlogSerializer):

    class Meta(BlogSerializer.Meta):
        pass

    def to_representation(self, instance):
        """
        Adds paginated blog posts
        """
        representation = super(BlogPostsSerializer, self).to_representation(instance)
        request = self.context.get('request')
        if request:
            paginator = PageNumberPagination()
            posts = paginator.paginate_queryset(instance.posts.filter(publish_date__lte=timezone.now()), request)
            serializer = BlogPostListSerializer(posts, many=True)
            representation['posts'] = OrderedDict([
                ('count', paginator.page.paginator.count),
                ('next', paginator.get_next_link()),
                ('previous', paginator.get_previous_link()),
                ('results', serializer.data)
            ])
        return representation
