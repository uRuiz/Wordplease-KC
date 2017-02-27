# -*- coding: utf-8 -*-
from blogs.models import Post
from django.forms import ModelForm


class PostForm(ModelForm):

    class Meta:
        model = Post
        exclude = ('blog',)
