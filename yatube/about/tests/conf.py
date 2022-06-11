from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


USER_STATUS = (
    'unauthorized',
    'authorized'
)

TEST_URL_STATUS = {
    '/about/author/': (HTTPStatus.OK, HTTPStatus.OK),
    '/about/tech/': (HTTPStatus.OK, HTTPStatus.OK),
    '/about/page-not-exist/': (HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND),
}

TEST_URL_TEMPLATE = {
    'unauthorized':
        {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        },
    'authorized':
        {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        },
}

TEST_VIEW_TMPLT = {
    'unauthorized':
        {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        },
    'authorized':
        {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        },
}

User = get_user_model()


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        """
        Create 2 users: unauthorized and authorized.
        """
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.clients = {
            'unauthorized': self.guest_client,
            'authorized': self.authorized_client,
        }
