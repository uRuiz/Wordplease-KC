# -*- coding: utf-8 -*-
from blogs.models import Blog
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class RelatedObjectDoesNotExist(object):
    pass


class SignupSerializer(UserSerializer):
    blog_name = serializers.CharField()
    blog_description = serializers.CharField()

    class Meta(UserSerializer.Meta):
        pass

    def update_user_with_blog_info(self, user, blog_name, blog_description):
        try:
            user.blog.name = blog_name
            user.blog.description = blog_description
            user.blog.save()
            user.blog_name = blog_name
            user.blog_description = blog_description
        except Blog.DoesNotExist:
            Blog.objects.create(owner=user, name=blog_name, description=blog_description)
            user.blog_name = blog_name
            user.blog_description = blog_description
        return user

    def extract_blog_data_and_encrypt_password(self, validated_data):
        blog_name = validated_data.pop('blog_name')
        blog_description = validated_data.pop('blog_description')
        password = validated_data.get('password')
        if password:
            validated_data['password'] = make_password(password)
        validated_data['is_active'] = True
        return (blog_name, blog_description)

    def create(self, validated_data):
        """
        Extracts the blog's data from validated data, creates the user and then creates the blog
        """
        blog_name, blog_description = self.extract_blog_data_and_encrypt_password(validated_data)
        user = super(UserSerializer, self).create(validated_data)
        if user:
            self.update_user_with_blog_info(user, blog_name, blog_description)
        return user

    def update(self, instance, validated_data):
        """
        Extracts the blog's data from validated data, updates the user and  the blog
        """
        blog_name, blog_description = self.extract_blog_data_and_encrypt_password(validated_data)
        user = super(UserSerializer, self).update(instance, validated_data)
        self.update_user_with_blog_info(user, blog_name, blog_description)
        return user