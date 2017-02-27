# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from users.views import SignupView, LogoutView, LoginView, ProfileView, ProfileUpdatedView, SignupSuccessfulView

urlpatterns = (
    url(r'^profile/?$', login_required(ProfileView.as_view()), name="users_profile"),
    url(r'^profile/updated?$', login_required(ProfileUpdatedView.as_view()), name="users_profile_updated"),
    url(r'^signup/?$', SignupView.as_view(), name="users_signup"),
    url(r'^signup/successful?$', SignupSuccessfulView.as_view(), name="users_signup_successful"),
    url(r'^login/?$', LoginView.as_view(), name="users_login"),
    url(r'^logout/?$', LogoutView.as_view(), name="users_logout")
)
