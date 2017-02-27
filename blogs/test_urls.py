# -*- coding: utf-8 -*-
from blogs.urls import urlpatterns as web_patterns
from blogs.api_urls import urlpatterns as api_patterns

urlpatterns = web_patterns + api_patterns
