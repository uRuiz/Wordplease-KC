# -*- coding: utf-8 -*-
from files.models import File
from files.permissions import FilePermission
from files.serializers import FileSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


class FileViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated, FilePermission)

    def perform_create(self, serializer):
        """
        Force auth user to be the file's owner
        """
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Force auth user to be the file's owner
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Returns logged user files or all if is superuser
        """
        return self.queryset if self.request.user.is_superuser else self.queryset.filter(owner=self.request.user)
