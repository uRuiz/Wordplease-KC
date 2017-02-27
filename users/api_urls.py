# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from users.api import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = (
    url(r'^1.0/', include(router.urls)),
)
