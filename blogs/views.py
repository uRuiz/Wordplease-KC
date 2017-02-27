from blogs.filters import PostFilter
from blogs.forms import PostForm
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.datetime_safe import datetime
from django.views.generic import ListView, DetailView, CreateView
from .models import Post, Blog, Category


class PostQueryset(object):

    def get_queryset(self):
        """
        Uses PostFilter to filter by category if needed
        """
        return PostFilter(
            self.request.GET, Post.objects.filter(publish_date__lte=datetime.now())
        ).qs.order_by('-publish_date')


class BlogContextData(object):

    @staticmethod
    def get_by_username(username):
        """
        Returns the blog contexts based in the username
        """
        return {
            'categories': Category.objects.all(),
            'username': username,
            'blog': get_object_or_404(Blog, owner__username=username)
        }


class PostDetail(PostQueryset, DetailView):
    template_name = 'blogs/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context.update(
            BlogContextData.get_by_username(self.kwargs.get('username'))
        )
        return context


class PostList(PostQueryset, ListView):
    template_name = 'blogs/latest_posts.html'
    paginate_by = 12


class BlogDetail(PostList):
    template_name = 'blogs/blog_detail.html'

    def get_queryset(self):
        return super(BlogDetail, self).get_queryset().filter(blog__owner__username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)
        context.update(
            BlogContextData.get_by_username(self.kwargs.get('username'))
        )
        return context


class BlogList(ListView):
    template_name = 'blogs/blog_list.html'
    queryset = Blog.objects.select_related('owner').annotate(
        posts_count=Count('posts')  # add a 'posts_count' attribute to every blog object counting the
    ).order_by('name')


class NewPost(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blogs/new_post.html'

    def get_success_url(self):
        """
        If everything is OK, we redirect the user to the new Post URL
        """
        post = self.object
        return reverse('post_detail', args=[post.blog.owner.username, post.pk])

    def get_form(self, form_class=None):
        """
        When the form is sent, set the post blog to the user blog
        """
        if self.request.method.upper() == "POST":
            form = super(NewPost, self).get_form(form_class)
            form.instance.blog = self.request.user.blog  # set the user blog
            return form
        else:
            return super(NewPost, self).get_form(form_class)
