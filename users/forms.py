# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    username = forms.CharField(label=_(u'Username'))
    password = forms.CharField(label=_(u'Password'), widget=forms.PasswordInput())

    def clean(self):
        user = authenticate(
            username=self.cleaned_data.get("username"),
            password=self.cleaned_data.get("password")
        )
        if not user:
            raise ValidationError(_(u'Wrong username or password'))
        else:
            self.cleaned_data['user'] = user


class UserForm(forms.Form):

    first_name = forms.CharField(label=_(u'First name'))
    last_name = forms.CharField(label=_(u'Last name'))
    email = forms.EmailField(label=_(u'E-mail'))
    username = forms.CharField(
        label=_(u'Username'),
        help_text=_(u'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[RegexValidator(
            r'[A-Za-z0-9@\.\+\-_]{1,30}',
            _(u'Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
        )]
    )
    password = forms.CharField(label=_(u'Password'), widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label=_(u'Confirm your password'), widget=forms.PasswordInput())
    blog_name = forms.CharField(label=_(u'Blog name'))
    blog_description = forms.CharField(label=_(u'Blog description'))

    def clean(self):
        existent_users = User.objects.filter(
            username=self.cleaned_data.get("username")
        )
        if len(existent_users) > 0 and self.instance not in existent_users:
            raise ValidationError(_(u'Username already exists'))

        if self.cleaned_data.get("password") != self.cleaned_data.get("password_confirmation"):
            raise ValidationError(_(u"Passwords don't match"))
