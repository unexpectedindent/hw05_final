from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from .conf import (PAGES_WITH_MULT_OBJ, TEMP_MEDIA_ROOT, TEST_POSTS_AMOUNT,
                   TEST_VIEW_TMPLT, TestConfig, USER_STATUS)
from ..forms import PostForm
from ..models import Follow, Group, Post


User = get_user_model()


class PostPagesTests(TestConfig):
    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_pages_uses_correct_template(self):
        """View-function uses correct template."""
        for user_case in USER_STATUS:
            for reverse_name, tmplate in TEST_VIEW_TMPLT[user_case].items():
                with self.subTest(reverse_name=reverse_name):
                    cache.clear()
                    response = self.clients[user_case].get(reverse_name)
                    self.assertTemplateUsed(
                        response,
                        tmplate,
                        ('Incorrect template for view-function '
                         f'{reverse_name} to {user_case}')
                    )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_correct_context_index_group_profile(self):
        """Check the context. 1st object has a correct attributes."""
        for reverse_name in PAGES_WITH_MULT_OBJ:
            cache.clear()
            response = self.clients['authorized'].get(reverse_name)
            first_object = response.context['page_obj'][0]
            attrs = {
                first_object.text: 'Тестовый пост',
                first_object.group.title: 'test_group',
                first_object.author.username: 'test_author',
                first_object.image.name: 'posts/small.gif'
            }
            for attr, value in attrs.items():
                with self.subTest():
                    self.assertEqual(attr, value)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_correct_context_post_detail(self):
        """Check the context for post detail."""
        reverse_name = reverse('posts:post_detail', kwargs={'post_id': '1'})
        cache.clear()
        response = self.clients['authorized'].get(reverse_name)
        post = response.context['post']
        attrs = {
            post.text: 'Тестовый пост',
            post.group.title: 'test_group',
            post.author.username: 'test_author',
            post.image.name: 'posts/small.gif'
        }
        for attr, value in attrs.items():
            with self.subTest():
                self.assertEqual(attr, value)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_correct_context_post_create_or_edit(self):
        """Check the context. Forms have correct attributes."""
        pages = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for page in pages:
            cache.clear()
            response = self.clients['author'].get(page)
            for val, expected in form_fields.items():
                with self.subTest(value=val):
                    form_fld = response.context.get('form').fields.get(val)
                    self.assertIsInstance(form_fld, expected)
                    self.assertIsInstance(
                        response.context['form'],
                        PostForm
                    )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_new_post(self):
        """Check a new post's location."""
        Group.objects.create(
            title='test_group2',
            slug='test-group2',
            description='description'
        )
        Post.objects.create(
            text='Тестовый пост2',
            author=PostPagesTests.user,
            group=Group.objects.get(title='test_group2')
        )
        pages = list(PAGES_WITH_MULT_OBJ) + [
            reverse('posts:group_list', kwargs={'slug': 'test-group2'})
        ]
        for page in pages:
            with self.subTest():
                cache.clear()
                response = self.clients['unauthorized'].get(page)
                page_obj = response.context['page_obj']
                if page != pages[1]:
                    self.assertIn(
                        Post.objects.get(text='Тестовый пост2'),
                        page_obj
                    )
                else:
                    self.assertNotIn(
                        Post.objects.get(text='Тестовый пост2'),
                        page_obj
                    )

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_cache(self):
        """Cache's testing."""
        response = self.clients['authorized'].get(reverse('posts:index'))
        old_page, old_posts_count = response.content, Post.objects.count()
        PostPagesTests.post.delete()
        response = self.clients['authorized'].get(reverse('posts:index'))
        new_page, new_posts_count = response.content, Post.objects.count()
        with self.subTest():
            self.assertEqual(old_page, new_page)
            self.assertNotEqual(old_posts_count, new_posts_count)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_follow(self):
        """Follow's testing."""
        Follow.objects.create(
            author=self.post_author,
            user=self.user
        )
        response = self.clients['authorized'].get(
            reverse('posts:follow_index')
        )
        page_obj = response.context['page_obj']
        with self.subTest():
            self.assertIn(
                Post.objects.get(pk=1),
                page_obj
            )
            Follow.objects.get(pk=1).delete()
            response = self.clients['authorized'].get(
                reverse('posts:follow_index')
            )
            page_obj = response.context['page_obj']
            self.assertNotIn(
                Post.objects.get(pk=1),
                page_obj
            )


class PaginatorViewsTest(TestCase):
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
        Post.objects.bulk_create(
            [Post(
                text='Тестовый пост',
                author=PaginatorViewsTest.user,
                group=PaginatorViewsTest.group,
            ) for _ in range(TEST_POSTS_AMOUNT)
            ]
        )

    def setUp(self):
        self.guest = Client()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_records_amount_are_on_page(self):
        """Paginator's testing."""
        cache.close()
        for reverse_name in PAGES_WITH_MULT_OBJ:
            page_count = (
                TEST_POSTS_AMOUNT // settings.SHOWN_POSTS_COUNT
                + int(bool(TEST_POSTS_AMOUNT % settings.SHOWN_POSTS_COUNT))
            )
            for page in range(page_count):
                response = self.guest.get(reverse_name, {'page': page + 1})
                with self.subTest():
                    if page + 1 < page_count:
                        self.assertEqual(
                            len(response.context['page_obj']),
                            settings.SHOWN_POSTS_COUNT
                        )
                    else:
                        self.assertEqual(
                            len(response.context['page_obj']),
                            TEST_POSTS_AMOUNT % settings.SHOWN_POSTS_COUNT
                        )
