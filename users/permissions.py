# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        """
        Gives permissions if the action is not list or user is superuser
        """
        return view.action != 'list' or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """
        Lets the user access to the profile is its superuser or if is its own profile
        """
        return request.user == obj or request.user.is_superuser
