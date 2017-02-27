# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class FilePermission(BasePermission):

    def has_permission(self, request, view):
        """
        Gives permissions if the action is not list or user is superuser
        """
        return True

    def has_object_permission(self, request, view, obj):
        """
        Lets the user access to the file detail if is its owner or superuser
        """
        return request.user == obj.owner or request.user.is_superuser
