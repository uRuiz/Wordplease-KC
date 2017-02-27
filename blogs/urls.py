# -*- coding: utf-8 -*-
from .views import PostList, BlogList, BlogDetail, PostDetail, NewPost
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(r'^$', PostList.as_view(), name="latest_posts"),
    url(r'^new-post/?$', login_required(NewPost.as_view()), name="new_post"),
    url(r'^blogs/?$', BlogList.as_view(), name="blog_list"),
    url(r'^blogs/(?P<username>[a-zA-Z0-9_]+)/?$', BlogDetail.as_view(), name="blog_detail"),
    url(r'^blogs/(?P<username>[a-zA-Z0-9_]+)/(?P<pk>[0-9]+)/?$', PostDetail.as_view(), name="post_detail"),
)