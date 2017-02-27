from blogs.models import Blog
from django.contrib.auth import logout, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.views.generic import RedirectView, FormView, TemplateView, View
from users.forms import UserForm, LoginForm


class SignupProfileView(View):

    template_name = None

    def get_form_initial_data(self, request):
        raise NotImplemented()

    def get_user_object(self):
        return User()

    def get_blog_object(self, user):
        return Blog(owner=user)

    def get_success_url(self):
        raise NotImplemented()

    def get(self, request):
        form = UserForm(initial=self.get_form_initial_data(request))
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user = self.get_user_object()
        form = UserForm(data=request.POST)
        form.instance = user
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.username = form.cleaned_data.get('username')
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            if request.user.is_authenticated():
                update_session_auth_hash(request, user)  # needed if we want to keep our session

            # Updating user blog info
            blog = self.get_blog_object(user)
            blog.name = form.cleaned_data.get('blog_name')
            blog.description = form.cleaned_data.get('blog_description')
            blog.save()
            return redirect(self.get_success_url())
        else:
            return render(request, self.template_name, {'form': form})


class SignupView(SignupProfileView):

    template_name = 'users/signup.html'

    def get_form_initial_data(self, request):
        return {}

    def get_success_url(self):
        return 'users_signup_successful'


class SignupSuccessfulView(TemplateView):
    template_name = 'users/signup_successful.html'


class ProfileView(SignupProfileView):
    template_name = 'users/profile.html'

    def get_form_initial_data(self, request):
        return {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'username': request.user.username,
            'blog_name': request.user.blog.name,
            'blog_description': request.user.blog.description
        }

    def get_user_object(self):
        return self.request.user

    def get_blog_object(self, user):
        return user.blog

    def get_success_url(self):
        return 'users_profile_updated'


class ProfileUpdatedView(TemplateView):
    template_name = 'users/profile_updated.html'


class LoginView(FormView):

    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        login(self.request, form.cleaned_data.get('user'))
        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next', reverse('users_profile'))


class LogoutView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return reverse('users_login')
