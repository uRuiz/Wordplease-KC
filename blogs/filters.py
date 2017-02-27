# -*- coding: utf-8 -*-
from blogs.models import Post
import django_filters


class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(name="categories")

    class Meta:
        model = Post
        fields = ['category']
