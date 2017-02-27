from blogs.models import Blog, Post
from blogs.models import Category
from django.contrib import admin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('title', 'image_url', 'intro', 'body', ('publish_date', 'blog'), 'categories')
    filter_horizontal = ('categories',)
    date_hierarchy = 'publish_date'
    search_fields = ('title', 'intro', 'body', 'blog__name')
    list_select_related = ('blog',)
    list_filter = ('categories', 'blog')
    list_display = ('title', 'blog', 'publish_date')
    save_as = True


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_select_related = ('owner',)
    list_display = ('name', 'owner')
    search_fields = ('name', 'owner__first_name', 'owner__last_name', 'owner__email', 'owner__username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

