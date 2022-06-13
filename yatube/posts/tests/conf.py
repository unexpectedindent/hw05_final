import os
import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..models import Group, Post


TEST_POSTS_AMOUNT = 13

USER_STATUS = (
    'unauthorized',
    'authorized',
    'author',
)

PAGES_WITH_POST = (
    reverse('posts:index'),
    reverse('posts:group_list', kwargs={'slug': 'test-group'}),
    reverse('posts:profile', kwargs={'username': 'test_author'},),
    reverse('posts:post_detail', kwargs={'post_id': '1'}),
)

PAGES_CREATE_OR_COMMENT = (
    reverse('posts:post_create'),
    reverse('posts:post_edit', kwargs={'post_id': '1'}),
)

TEST_URL_STATUS = {
    '/': (HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.OK),
    '/group/test-group/': (HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.OK),
    '/group/test-group-not-exist/': (HTTPStatus.NOT_FOUND,
                                     HTTPStatus.NOT_FOUND,
                                     HTTPStatus.NOT_FOUND),
    '/profile/test_author/': (HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.OK),
    '/posts/1/': (HTTPStatus.OK, HTTPStatus.OK, HTTPStatus.OK),
    '/posts/2/': (HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND,
                  HTTPStatus.NOT_FOUND),
    '/create/': (HTTPStatus.FOUND, HTTPStatus.OK, HTTPStatus.OK),
    '/posts/1/edit/': (HTTPStatus.FOUND, HTTPStatus.FOUND, HTTPStatus.OK),
    '/follow/': (HTTPStatus.FOUND, HTTPStatus.OK, HTTPStatus.OK),
    '/profile/test_author/follow/': (HTTPStatus.FOUND,
                                     HTTPStatus.FOUND,
                                     HTTPStatus.FOUND),
    '/profile/test_author/unfollow/': (HTTPStatus.FOUND,
                                       HTTPStatus.FOUND,
                                       HTTPStatus.FOUND),
    '/posts/1/comment/': (HTTPStatus.FOUND,
                          HTTPStatus.FOUND,
                          HTTPStatus.FOUND),
    '/posts/1/delete/': (HTTPStatus.FOUND, HTTPStatus.FOUND,
                         HTTPStatus.FOUND),
}

REDIRECTS = {
    'unauthorized':
        {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/posts/1/delete/': '/auth/login/?next=/posts/1/delete/',
            '/profile/test_author/follow/':
                '/auth/login/?next=/profile/test_author/follow/',
            '/profile/test_author/unfollow/':
                '/auth/login/?next=/profile/test_author/unfollow/',
            '/posts/1/comment/': '/auth/login/?next=/posts/1/comment/',
            '/follow/': '/auth/login/?next=/follow/',
        },
    'authorized':
        {
            '/posts/1/edit/': '/posts/1/',
            '/posts/1/delete/': '/posts/1/',
            '/posts/1/comment/': '/posts/1/',
            '/profile/test_author/follow/': '/profile/test_author/',
            '/profile/test_author/unfollow/': '/profile/test_author/'
        },
    'author':
        {
            '/posts/1/comment/': '/posts/1/',
            '/profile/test_author/follow/': '/profile/test_author/',
            '/profile/test_author/unfollow/': '/profile/test_author/',
            '/posts/1/delete/': '/profile/test_author/',
        }
}

TEST_URL_TEMPLATE = {
    'unauthorized':
        {
            '/': 'posts/index.html',
            '/group/test-group/': 'posts/group_list.html',
            '/profile/test_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html'
        },
    'authorized':
        {
            '/': 'posts/index.html',
            '/group/test-group/': 'posts/group_list.html',
            '/profile/test_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        },
    'author':
        {
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
}

TEST_VIEW_TMPLT = {
    'unauthorized':
        {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-group'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'test_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            ): 'posts/post_detail.html'
        },
    'authorized':
        {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-group'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'test_author'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        },
    'author':
        {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            ): 'posts/create_post.html'
        }
}

IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(
    dir=os.path.dirname(os.path.abspath(__file__))
)


class TestConfig(TestCase):
    @classmethod
    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-group',
            description='test description'
        )
        cls.post = Post.objects.create(
            text='text_text_text_text',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """
        Create 3 users: unauthorized, authorized, authorized post's author.
        """
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.post_author = User.objects.get(username='test_author')
        self.author.force_login(self.post_author)
        self.clients = {
            'unauthorized': self.guest_client,
            'authorized': self.authorized_client,
            'author': self.author
        }
        self.users = {
            self.authorized_client: self.user,
            self.author: self.post_author
        }
