# -*- coding: utf-8 -*-
from rest_framework import permissions


class PostPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Let to access the object if action is retrieve or user is superuser or post's owner
        """
        return view.action == 'retrieve' or request.user.is_superuser or request.user == obj.blog.owner
