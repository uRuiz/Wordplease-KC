from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(ROOT_URLCONF='users.api_urls')
class UserAPITest(APITestCase):
    pass


class SignupAPITest(UserAPITest):

    def test_all_fields_required(self):
        """
        Ensure that all required fields are required
        """
        data_to_send = {
            'first_name': 'Django',
            'last_name': 'Reinhardt',
            'email': 'django@reinhardt.com',
            'username': 'reinhardt',
            'password': 'cmon',
            'blog_name': 'Django\'s Blog',
            'blog_description': 'Another test blog'
        }
        data = {}
        latest = ('', '')
        for key in data_to_send:
            response = self.client.post('/1.0/users/', data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertNotIn(latest[0], response.data)
            latest = (key, data_to_send[key])
            data[latest[0]] = latest[1]
        response = self.client.post('/1.0/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in data:
            if key == 'password':
                continue  # cannot check a encrypted password
            self.assertEqual(response.data.get(key), data.get(key))

    def test_created_user_can_login(self):
        """
        Ensure that the user can login after its signup
        """
        data = {
            'first_name': 'Django',
            'last_name': 'Reinhardt',
            'email': 'django@reinhardt.com',
            'username': 'reinhardt',
            'password': 'cmon',
            'blog_name': 'Django\'s Blog',
            'blog_description': 'Another test blog'
        }
        response = self.client.post('/1.0/users/', data)
        user = authenticate(username=data.get('username'), password=data.get('password'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = authenticate(username=data.get('username'), password=data.get('password'))
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, data.get('first_name'))
        self.assertEqual(user.last_name, data.get('last_name'))
        self.assertEqual(user.email, data.get('email'))
        self.assertEqual(user.username, data.get('username'))

    def test_created_user_blog_is_properly_created(self):
        """
        Ensure that the user blog data is properly created
        """
        data = {
            'first_name': 'Django',
            'last_name': 'Reinhardt',
            'email': 'django@reinhardt.com',
            'username': 'reinhardt',
            'password': 'cmon',
            'blog_name': 'Django\'s Blog',
            'blog_description': 'Another test blog'
        }
        response = self.client.post('/1.0/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = authenticate(username=data.get('username'), password=data.get('password'))
        self.assertIsNotNone(user)
        self.assertEqual(user.blog.name, data.get('blog_name'))
        self.assertEqual(user.blog.description, data.get('blog_description'))

    def test_reject_used_username(self):
        """
        Ensure that a username cannot be used twice
        """
        data = {
            'first_name': 'Django',
            'last_name': 'Reinhardt',
            'email': 'django@reinhardt.com',
            'username': 'reinhardt',
            'password': 'cmon',
            'blog_name': 'Django\'s Blog',
            'blog_description': 'Another test blog'
        }
        response = self.client.post('/1.0/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post('/1.0/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAPITestWithUsers(UserAPITest):

    def setUp(self):
        self.users = [
            {'username': 'django', 'email': 'django@wordplease.com', 'password': 'dissilent', 'is_superuser': True},
            {'username': 'schultz', 'email': 'schultz@wordplease.com', 'password': 'doctor', 'is_superuser': False},
            {'username': 'calvin', 'email': 'calvin@wordplease.com', 'password': 'candie', 'is_superuser': False}
        ]
        for user in self.users:
            if user.get('is_superuser'):
                User.objects.create_superuser(user.get('username'), user.get('email'), user.get('password'))
            else:
                User.objects.create_user(user.get('username'), user.get('email'), user.get('password'))


class UserDetailAPITest(UserAPITestWithUsers):

    def test_anonymous_user_cannot_see_any_profile(self):
        """
        Ensure that an anonymous user cannot see any profiles
        """
        for user in User.objects.all():
            response = self.client.get('/1.0/users/{0}/'.format(user.pk))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_see_its_profile_and_cannot_other_profiles(self):
        """
        Ensure that a user can see its profile but cannot see other profiles
        """
        NO_SUPERUSER = 1
        self.client.login(
            username=self.users[NO_SUPERUSER].get('username'),
            password=self.users[NO_SUPERUSER].get('password')
        )
        for user in User.objects.all():
            response = self.client.get('/1.0/users/{0}/'.format(user.pk))
            if user.username == self.users[NO_SUPERUSER].get('username'):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_see_any_profile(self):
        """
        Ensure that a superuser can see any profile
        """
        SUPERUSER = 0
        self.client.login(
            username=self.users[SUPERUSER].get('username'),
            password=self.users[SUPERUSER].get('password')
        )
        for user in User.objects.all():
            response = self.client.get('/1.0/users/{0}/'.format(user.pk))
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserUpdateAPITest(UserAPITestWithUsers):

    def test_anonymous_user_cannot_update_any_profile(self):
        """
        Ensure that an anonymous user cannot update any profiles
        """
        data = {
            'first_name': 'Django',
            'last_name': 'Fake',
            'email': 'django@fake.com',
            'username': 'fake',
            'password': 'cmon',
            'blog_name': 'Django Fake\'s Blog',
            'blog_description': 'Another test blog'
        }
        for user in User.objects.all():
            response = self.client.put('/1.0/users/{0}/'.format(user.pk), data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_update_its_profile_and_cannot_other_profiles(self):
        """
        Ensure that a user can update its profile but cannot delete other profiles
        """
        NO_SUPERUSER = 1
        self.client.login(
            username=self.users[NO_SUPERUSER].get('username'),
            password=self.users[NO_SUPERUSER].get('password')
        )
        data = {
            'first_name': 'Django',
            'last_name': 'Fake',
            'email': 'django@fake.com',
            'username': 'fake',
            'password': 'cmon',
            'blog_name': 'Django Fake\'s Blog',
            'blog_description': 'Another test blog'
        }
        for user in User.objects.all():
            response = self.client.put('/1.0/users/{0}/'.format(user.pk), data)
            if user.username == self.users[NO_SUPERUSER].get('username'):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                for key in data:
                    if key == 'password':
                        continue  # cannot check a encrypted password
                    self.assertEqual(data.get(key), response.data.get(key))
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_delete_update_profile(self):
        """
        Ensure that a superuser can update any profile
        """
        SUPERUSER = 0
        self.client.login(
            username=self.users[SUPERUSER].get('username'),
            password=self.users[SUPERUSER].get('password')
        )
        data = {
            'first_name': 'Django',
            'last_name': 'Fake',
            'email': 'django@fake.com',
            'username': 'fake',
            'password': 'cmon',
            'blog_name': 'Django Fake\'s Blog',
            'blog_description': 'Another test blog'
        }
        for user in User.objects.all():
            if user.username == self.users[SUPERUSER].get('username'):  # skips to delete its profile but keeps its ID
                superuser_ID = user.pk
                continue
            data['username'] = user.username + '_1'
            data['email'] = user.email + '.es'
            response = self.client.put('/1.0/users/{0}/'.format(user.pk), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # superuser deletes its profile
        data['username'] = 'superuser'
        data['email'] = 'super@user.com'
        response = self.client.put('/1.0/users/{0}/'.format(superuser_ID), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserDeleteAPITest(UserAPITestWithUsers):

    def test_anonymous_user_cannot_delete_any_profile(self):
        """
        Ensure that an anonymous user cannot delete any profiles
        """
        for user in User.objects.all():
            response = self.client.delete('/1.0/users/{0}/'.format(user.pk))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_delete_its_profile_and_cannot_other_profiles(self):
        """
        Ensure that a user can delete its profile but cannot delete other profiles
        """
        NO_SUPERUSER = 1
        self.client.login(
            username=self.users[NO_SUPERUSER].get('username'),
            password=self.users[NO_SUPERUSER].get('password')
        )
        for user in User.objects.all():
            response = self.client.delete('/1.0/users/{0}/'.format(user.pk))
            if user.username == self.users[NO_SUPERUSER].get('username'):
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            else:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_delete_any_profile(self):
        """
        Ensure that a superuser can delete any profile
        """
        SUPERUSER = 0
        self.client.login(
            username=self.users[SUPERUSER].get('username'),
            password=self.users[SUPERUSER].get('password')
        )
        for user in User.objects.all():
            if user.username == self.users[SUPERUSER].get('username'):  # skips to delete its profile but keeps its ID
                superuser_ID = user.pk
                continue
            response = self.client.delete('/1.0/users/{0}/'.format(user.pk))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # superuser deletes its profile
        response = self.client.delete('/1.0/users/{0}/'.format(superuser_ID))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UserListAPITest(UserAPITestWithUsers):

    def test_anonymous_user_cannot_access_users_list(self):
        """
        Ensure that an anonymous user cannot access the users list
        """
        response = self.client.get('/1.0/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_plain_user_cannot_access_users_list(self):
        """
        Ensure that a plain user cannot access the users list
        """
        NO_SUPERUSER = 1
        self.client.login(
            username=self.users[NO_SUPERUSER].get('username'),
            password=self.users[NO_SUPERUSER].get('password')
        )
        response = self.client.get('/1.0/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_access_users_list(self):
        """
        Ensure that superuser can access the users list
        """
        SUPERUSER = 0
        self.client.login(
            username=self.users[SUPERUSER].get('username'),
            password=self.users[SUPERUSER].get('password')
        )
        response = self.client.get('/1.0/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data.get('results'):
            db_user = User.objects.get(pk=user.get('id'))
            self.assertIsNotNone(db_user)
