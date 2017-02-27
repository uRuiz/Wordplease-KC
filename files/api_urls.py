# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from files.api import FileViewSet

router = DefaultRouter()
router.register('files', FileViewSet)

urlpatterns = (
    url(r'^1.0/', include(router.urls)),
)
