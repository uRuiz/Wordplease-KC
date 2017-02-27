from datetime import timedelta, datetime

from django.test import override_settings
from django.utils import timezone
from blogs.models import Blog, Post, Category
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(ROOT_URLCONF='blogs.test_urls')
class BlogsModuleTests(APITestCase):
    pass


class BlogAPITests(BlogsModuleTests):

    def setUp(self):
        User.objects.bulk_create([
            User(
                first_name="User",
                last_name="One",
                username="user_one",
                email="user_one@wordplease.com",
                password="wordplease"
            ),
            User(
                first_name="User",
                last_name="Two",
                username="user_two",
                email="user_two@wordplease.com",
                password="wordplease"
            )
        ])

        for user in User.objects.all():
            Blog.objects.create(
                owner=user,
                name='{0} {1}\'s blog'.format(user.first_name, user.last_name),
                description='Just another blog in Wordplease'
            )

    def test_blog_list_without_authentication(self):
        """
        Ensure that authentication is not required to get the blogs list
        """
        response = self.client.get('/1.0/blogs/')
        self.assertEqual(response.data.get('count'), 2)

    def test_search_blog_by_owner_username(self):
        """
        Ensure that lets search blogs by its owner username
        """
        response = self.client.get('/1.0/blogs/?search=one')
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('name'), "User One's blog")
        response = self.client.get('/1.0/blogs/?search=two')
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('name'), "User Two's blog")

    def test_order_blog_by_name(self):
        """
        Ensure that lets order blogs by name
        """
        response = self.client.get('/1.0/blogs/?ordering=name')
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(response.data.get('results')[0].get('name'), "User One's blog")
        response = self.client.get('/1.0/blogs/?ordering=-name')
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(response.data.get('results')[0].get('name'), "User Two's blog")


class PostsAPITests(BlogsModuleTests):

    def setUp(self):
        self.user = User.objects.create_user("mindundi", "user@wordplease", "supersecretpassword")
        self.user.raw_password = "supersecretpassword"
        self.superuser = User.objects.create_user("admin", "admin@wordplease", "ultrasecretpassword")
        self.superuser.is_superuser = True
        self.superuser.save()
        self.superuser.raw_password = "ultrasecretpassword"

        blog1 = Blog.objects.create(
            owner=self.superuser,
            name="Blog One",
            description="Blog One Description"
        )
        blog2 = Blog.objects.create(
            owner=self.user,
            name="Blog Two",
            description="Blog Two Description"
        )

        self.post1 = Post.objects.create(
            blog=blog1,
            title="Post in the past in the blog one title",
            intro="Post in the past in the blog one intro",
            body="Post in the past in the blog one body",
            publish_date=timezone.make_aware(datetime.now() - timedelta(days=20), timezone.get_current_timezone())
        )
        self.post2 = Post.objects.create(
            blog=blog1,
            title="Post in the future in the blog one title",
            intro="Post in the future in the blog one intro",
            body="Post in the future in the blog one body",
            publish_date=timezone.make_aware(datetime.now() + timedelta(days=10), timezone.get_current_timezone())
        )
        self.post3 = Post.objects.create(
            blog=blog2,
            title="Post in the past in the blog two title",
            intro="Post in the past in the blog two intro",
            body="Post in the past in the blog two body",
            publish_date=timezone.make_aware(datetime.now() - timedelta(days=10), timezone.get_current_timezone())
        )
        self.post4 = Post.objects.create(
            blog=blog2,
            title="Post in the future in the blog two title",
            intro="Post in the future in the blog two intro",
            body="Post in the future in the blog two body",
            publish_date=timezone.make_aware(datetime.now() + timedelta(days=20), timezone.get_current_timezone())
        )

        self.category1 = Category.objects.create(name="Category One")
        self.category1.posts.add(self.post1, self.post4)

        self.category2 = Category.objects.create(name="Category Two")
        self.category2.posts.add(self.post2, self.post3)

        self.category3 = Category.objects.create(name="Category Three")
        self.category3.posts.add(self.post1, self.post2, self.post3, self.post4)


class PostListAPITests(PostsAPITests):

    def assertPostsEqual(self, data, posts):
        posts_titles = [item.get('title') for item in data]
        self.assertEqual(
            sorted(posts_titles),
            sorted(posts)
        )

    def test_no_auth_user_only_see_published_posts(self):
        """
        Ensure that a non auth request only returns published posts
        """
        response = self.client.get('/1.0/posts/')
        self.assertEqual(response.data.get('count'), 2)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title, self.post3.title])

    def test_superuser_can_see_all_posts(self):
        """
        Ensure that a superuser can see all posts
        """
        self.client.login(
            username=self.superuser.username,
            password=self.superuser.raw_password
        )
        response = self.client.get('/1.0/posts/')
        self.assertEqual(len(response.data), 4)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title, self.post2.title, self.post3.title, self.post4.title])

    def test_normal_user_can_see_its_posts_and_others_published(self):
        """
        Ensure that a user can see its own posts and the others published
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        response = self.client.get('/1.0/posts/')
        self.assertEqual(response.data.get('count'), 3)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title, self.post3.title, self.post4.title])

    def test_search_posts_by_title_or_content(self):
        """
        Ensure that can search by title or content and founds what it has to found
        """
        response = self.client.get('/1.0/posts/?search=one+title')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title])
        response = self.client.get('/1.0/posts/?search=one+intro')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title])
        response = self.client.get('/1.0/posts/?search=one+body')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post1.title])
        response = self.client.get('/1.0/posts/?search=one+bam')
        self.assertEqual(response.data.get('count'), 0)

        response = self.client.get('/1.0/posts/?search=two+title')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post3.title])
        response = self.client.get('/1.0/posts/?search=two+intro')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post3.title])
        response = self.client.get('/1.0/posts/?search=two+body')
        self.assertEqual(response.data.get('count'), 1)
        self.assertPostsEqual(response.data.get('results'), [self.post3.title])
        response = self.client.get('/1.0/posts/?search=two+bam')
        self.assertEqual(response.data.get('count'), 0)

    def test_order_by_title_and_publish_date(self):
        """
        Ensure that can order by title and publish_date
        """
        response = self.client.get('/1.0/posts/?ordering=title')
        posts_titles = [item.get('title') for item in response.data.get('results')]
        self.assertEqual(response.data.get('count'), 2)
        self.assertListEqual(posts_titles, [self.post1.title, self.post3.title])

        response = self.client.get('/1.0/posts/?ordering=-title')
        posts_titles = [item.get('title') for item in response.data.get('results')]
        self.assertEqual(response.data.get('count'), 2)
        self.assertListEqual(posts_titles, [self.post3.title, self.post1.title])

        response = self.client.get('/1.0/posts/?ordering=publish_date')
        posts_titles = [item.get('title') for item in response.data.get('results')]
        self.assertEqual(response.data.get('count'), 2)
        self.assertListEqual(posts_titles, [self.post1.title, self.post3.title])

        response = self.client.get('/1.0/posts/?ordering=-publish_date')
        posts_titles = [item.get('title') for item in response.data.get('results')]
        self.assertEqual(response.data.get('count'), 2)
        self.assertListEqual(posts_titles, [self.post3.title, self.post1.title])


class PostCreateAPITest(PostsAPITests):

    def test_user_must_be_authenticated(self):
        """
        Ensures that the user must be authenticated to create a post
        """
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/'
        }
        response = self.client.post('/1.0/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_must_be_in_user_blog(self):
        """
        Ensures that a post is published in the authenticated user's blog
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/',
            'categories': [self.category1.pk]
        }
        response = self.client.post('/1.0/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in data:
            self.assertIsNotNone(response.data.get(key))
            self.assertEqual(response.data.get(key), data.get(key))
        new_post = Post.objects.get(pk=response.data.get('id'))
        self.assertEqual(new_post.blog.pk, self.user.blog.pk)


class PostDetailAPITest(PostsAPITests):

    def test_public_post_can_be_accessed_by_anyone(self):
        """
        Ensures that a public post (future post) can be accessed by anyone
        """
        post_to_check = self.post3
        response = self.client.get('/1.0/posts/{0}/'.format(post_to_check.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), post_to_check.id)

    def test_not_public_post_can_be_accessed_by_anyone(self):
        """
        Ensures that a not public post (future post) cannot be accessed by anyone
        """
        post_to_check = self.post4
        response = self.client.get('/1.0/posts/{0}/'.format(post_to_check.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_public_post_can_be_accessed_by_the_blog_owner(self):
        """
        Ensures that a not public post (future post) can be accessed by its owner
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        post_to_check = self.post4
        response = self.client.get('/1.0/posts/{0}/'.format(post_to_check.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), post_to_check.id)

    def test_not_public_post_can_be_accessed_by_superuser(self):
        """
        Ensures that a not public post (future post) can be accessed by a superuser
        """
        self.client.login(
            username=self.superuser.username,
            password=self.superuser.raw_password
        )
        post_to_check = self.post4
        response = self.client.get('/1.0/posts/{0}/'.format(post_to_check.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), post_to_check.id)


class PostUpdateAPITest(PostsAPITests):

    def test_post_cannot_be_updated_by_anonymous(self):
        """
        Ensures that a post cannot be updated by anonymous user
        """
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/'
        }
        post_to_update = self.post1
        response = self.client.put('/1.0/posts/{0}/'.format(post_to_update.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_cannot_be_updated_by_other(self):
        """
        Ensures that a post cannot be updated by other
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/'
        }
        post_to_update = self.post1
        response = self.client.put('/1.0/posts/{0}/'.format(post_to_update.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_can_be_updated_by_its_author(self):
        """
        Ensures that a post can be updated by its author
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/',
            'categories': [self.category1.pk]
        }
        post_to_update = self.post3
        response = self.client.put('/1.0/posts/{0}/'.format(post_to_update.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), post_to_update.id)
        self.assertEqual(response.data.get('blog').get('id'), post_to_update.blog.id)
        for key in data:
            self.assertEqual(data.get(key), response.data.get(key))

    def test_post_can_be_updated_by_a_superuser(self):
        """
        Ensures that a post can be updated by a superuser
        """
        self.client.login(
            username=self.superuser.username,
            password=self.superuser.raw_password
        )
        data = {
            'title': 'Lorem ipsum',
            'intro': 'Lorem ipsum dolor',
            'body': 'Lorem ipsum dolor sit amet',
            'image_url': 'http://example.com/',
            'categories': [self.category1.pk]
        }
        post_to_update = self.post3
        response = self.client.put('/1.0/posts/{0}/'.format(post_to_update.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), post_to_update.id)
        self.assertEqual(response.data.get('blog').get('id'), post_to_update.blog.id)
        for key in data:
            self.assertEqual(data.get(key), response.data.get(key))


class PostDeleteAPITest(PostsAPITests):

    def test_post_cannot_be_deleted_by_anonymous(self):
        """
        Ensures that a post cannot be deleted by anonymous user
        """
        post_to_delete = self.post1
        response = self.client.delete('/1.0/posts/{0}/'.format(post_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_cannot_be_deleted_by_other(self):
        """
        Ensures that a post cannot be deleted by other
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        post_to_delete = self.post1
        response = self.client.delete('/1.0/posts/{0}/'.format(post_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_can_be_deleted_by_its_author(self):
        """
        Ensures that a post can be deleted by its author
        """
        self.client.login(
            username=self.user.username,
            password=self.user.raw_password
        )
        post_to_delete = self.post3
        response = self.client.delete('/1.0/posts/{0}/'.format(post_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_can_be_deleted_by_a_superuser(self):
        """
        Ensures that a post can be deleted by a superuser
        """
        self.client.login(
            username=self.superuser.username,
            password=self.superuser.raw_password
        )
        post_to_delete = self.post3
        response = self.client.delete('/1.0/posts/{0}/'.format(post_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PostListFilterAPITest(PostsAPITests):

    def test_category_filter(self):
        """
        Ensure that the post list category filter works properly
        """
        response = self.client.get('/1.0/posts/?category={0}'.format(self.category1.pk))
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(sorted(map(lambda item: item.get('id'), response.data.get('results'))), sorted([self.post1.pk]))

        response = self.client.get('/1.0/posts/?category={0}'.format(self.category2.pk))
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(sorted(map(lambda item: item.get('id'), response.data.get('results'))), sorted([self.post3.pk]))

        response = self.client.get('/1.0/posts/?category={0}'.format(self.category3.pk))
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(
            sorted(map(lambda item: item.get('id'), response.data.get('results'))),
            sorted([self.post1.pk, self.post3.pk])
        )

    def test_category_filter_with_superuser(self):
        """
        Ensure that the post list category filter works properly with a supersuer who can see everything
        """
        self.client.login(
            username=self.superuser.username,
            password=self.superuser.raw_password
        )

        response = self.client.get('/1.0/posts/?category={0}'.format(self.category1.pk))
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(
            sorted(map(lambda item: item.get('id'), response.data.get('results'))),
            sorted([self.post1.pk, self.post4.pk])
        )

        response = self.client.get('/1.0/posts/?category={0}'.format(self.category2.pk))
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(
            sorted(map(lambda item: item.get('id'), response.data.get('results'))),
            sorted([self.post2.pk, self.post3.pk])
        )

        response = self.client.get('/1.0/posts/?category={0}'.format(self.category3.pk))
        self.assertEqual(response.data.get('count'), 4)
        self.assertEqual(
            sorted(map(lambda item: item.get('id'), response.data.get('results'))),
            sorted([self.post1.pk, self.post2.pk, self.post3.pk, self.post4.pk])
        )


class PostCountAPITest(PostsAPITests):

    def test_post_count_in_posts_list(self):
        """
        Ensure that the posts count works in posts list
        """
        response = self.client.get('/1.0/blogs/')
        for blog in response.data.get('results'):
            self.assertEqual(blog.get('posts_count'), Post.objects.filter(blog__id=blog.get('id')).count())
