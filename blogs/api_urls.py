# -*- coding: utf-8 -*-
from blogs.api import BlogsViewSet, PostsViewSet
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('blogs', BlogsViewSet)
router.register('posts', PostsViewSet)

urlpatterns = (
    url(r'^1.0/', include(router.urls)),
)
