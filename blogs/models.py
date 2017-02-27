import sys
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .tasks import download_resize_update_photo_image
from .settings import DOWNLOAD_IMAGES


class Category(models.Model):

    name = models.CharField(max_length=250, primary_key=True)

    class Meta:
        verbose_name_plural = "categories"

    def __unicode__(self):
        return self.name


class Blog(models.Model):
    owner = models.OneToOneField(User, related_name="blog")  # Ensures that a user only have one blog
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250, blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """
        Returns the Blog's absolute URL and shows a "Visit on site" button in admin's Blog detail.
        :return: string with the Blog's absolute URL
        """
        return reverse('blog_detail', args=[self.owner.username])

    def __unicode__(self):
        return self.name


class Post(models.Model):
    blog = models.ForeignKey(Blog, related_name="posts")  # Allows access to posts from Blogs.posts instead of Blogs.post_set
    title = models.CharField(max_length=250)
    intro = models.TextField(max_length=250)
    body = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    publish_date = models.DateTimeField(default=timezone.now)  # Sets automatically the time to now, by let us to modify the value if we want
    categories = models.ManyToManyField(Category, related_name="posts")  # Allows access to posts from Category.posts instead of Blogs.category_set

    def get_absolute_url(self):
        """
        Returns the Post's absolute URL and shows a "Visit on site" button in admin's Post detail.
        :return: string with the Post's absolute URL
        """
        return reverse('post_detail', args=[self.blog.owner.username, self.pk])

    def get_author(self):
        """
        Returns the Post's author throught the post blog's owner
        """
        return '{0} {1}'.format(self.blog.owner.first_name, self.blog.owner.last_name)

    def __unicode__(self):
        return self.title


# avoids to set the signal if we are testing
if settings.USE_CELERY and 'test' not in sys.argv and 'migrate' not in sys.argv and DOWNLOAD_IMAGES:

    @receiver(post_save, sender=Post)
    def download_image_on_save(sender, **kwargs):
        post = kwargs.get('instance')
        if post and settings.BASE_URL not in post.image_url:
            download_resize_update_photo_image.delay(post)
