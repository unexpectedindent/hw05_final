from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from .conf import (
    IMAGE, PAGES_CREATE_OR_COMMENT, PAGES_WITH_POST, TEMP_MEDIA_ROOT,
    TEST_POSTS_AMOUNT, TEST_VIEW_TMPLT, TestConfig, USER_STATUS
)
from ..forms import CommentForm, PostForm
from ..models import Comment, Follow, Group, Post


User = get_user_model()


class PostImagesTests(TestConfig):
    @classmethod
    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def setUpClass(cls):
        super().setUpClass()
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=IMAGE,
            content_type='image/gif'
        )
        cls.post.image = cls.uploaded
        cls.post.save()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_image(self):
        """Check image is on the pages."""
        for reverse_name in PAGES_WITH_POST:
            cache.clear()
            context = self.clients['authorized'].get(reverse_name).context
            if 'page_obj' in context:
                obj = context['page_obj'][0]
            else:
                obj = context['post']
            attrs = {
                obj.image.name: 'posts/small.gif'
            }
            for attr, value in attrs.items():
                with self.subTest(attr=attr, reverse_name=reverse_name):
                    self.assertEqual(attr, value)


class PostPagesTests(TestConfig):
    def test_pages_uses_correct_template(self):
        """View-function uses correct template."""
        for user_case in USER_STATUS:
            for reverse_name, tmplate in TEST_VIEW_TMPLT[user_case].items():
                with self.subTest(
                    reverse_name=reverse_name,
                    user_case=user_case
                ):
                    cache.clear()
                    response = self.clients[user_case].get(reverse_name)
                    self.assertTemplateUsed(response, tmplate)

    def test_correct_context_index_group_profile(self):
        """Check the context: object has a correct attributes."""
        for reverse_name in PAGES_WITH_POST:
            cache.clear()
            context = self.clients['authorized'].get(reverse_name).context
            if 'page_obj' in context:
                obj = context['page_obj'][0]
            else:
                obj = context['post']
            attrs = {
                obj.text: PostPagesTests.post.text,
                obj.group.title: PostPagesTests.post.group.title,
                obj.author.username: PostPagesTests.post.author.username
            }
            for attr, value in attrs.items():
                with self.subTest(attr=attr, reverse_name=reverse_name):
                    self.assertEqual(attr, value)

    def test_correct_context_post_create_or_edit(self):
        """Check the context: forms have the correct attributes."""
        form_fields = {
            'text': forms.fields.CharField,
        }
        for page in PAGES_CREATE_OR_COMMENT:
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

    def test_correct_context_post_comment(self):
        """Check the context: form has the correct attributes."""
        page = reverse('posts:post_detail', kwargs={'post_id': '1'})
        form_fields = {'text': forms.fields.CharField}
        cache.clear()
        response = self.clients['author'].get(page)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(
                    response.context['form'],
                    CommentForm
                )

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
        pages = list(PAGES_WITH_POST) + [
            reverse('posts:group_list', kwargs={'slug': 'test-group2'})
        ]
        pages.remove(reverse('posts:post_detail', kwargs={'post_id': '1'}))
        for page in pages:
            with self.subTest(page=page):
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

    def test_unauthorized_cannot_create_comment(self):
        """Test anonymous user can not create comment."""
        user = AnonymousUser()
        with self.assertRaises(ValueError):
            Comment.objects.create(
                post=Post.objects.get(pk=1),
                author=user,
                text='comment'
            )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_author')
        Post.objects.bulk_create(
            [Post(
                text=f'{number}_text_text_text_text',
                author=PaginatorViewsTest.user,
            ) for number in range(TEST_POSTS_AMOUNT)
            ]
        )

    def setUp(self):
        self.guest = Client()

    def test_records_amount_are_on_page(self):
        """Paginator's testing."""
        cache.close()
        reverse_name = reverse('posts:index')
        page_count = (
            TEST_POSTS_AMOUNT // settings.SHOWN_POSTS_COUNT
            + int(bool(TEST_POSTS_AMOUNT % settings.SHOWN_POSTS_COUNT))
        )
        for page in range(page_count):
            response = self.guest.get(reverse_name, {'page': page + 1})
            with self.subTest(page=page):
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


class PostFollow(TestConfig):
    def setUp(self):
        super().setUp()
        self.nonfollower = User.objects.create_user(
            username='nonfollower'
        )
        self.auth_nonfollower = Client()
        self.auth_nonfollower.force_login(self.nonfollower)

    def test_follow(self):
        """Follow's testing."""
        response = self.clients['authorized'].get(
            reverse('posts:follow_index')
        )
        page_obj = response.context['page_obj']
        self.assertNotIn(
            Post.objects.get(pk=1),
            page_obj,
            'Post is shown for non-follower'
        )
        self.clients['authorized'].get(reverse(
            'posts:profile_follow',
            kwargs={'username': 'test_author'}
        ))
        response = self.clients['authorized'].get(
            reverse('posts:follow_index')
        )
        page_obj = response.context['page_obj']
        self.assertIn(
            Post.objects.get(pk=1),
            page_obj,
            'Post is not show for follower'
        )

    def test_unfollow(self):
        """Unfollow's testing."""
        Follow.objects.create(author=self.post_author, user=self.user)
        response = self.clients['authorized'].get(
            reverse('posts:follow_index')
        )
        page_obj = response.context['page_obj']
        self.assertIn(
            Post.objects.get(pk=1),
            page_obj,
            'Post is not shown for follower'
        )
        self.clients['authorized'].get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': 'test_author'}
        ))
        response = self.clients['authorized'].get(
            reverse('posts:follow_index')
        )
        page_obj = response.context['page_obj']
        self.assertNotIn(
            Post.objects.get(pk=1),
            page_obj,
            'Post is shown for non-follower'
        )

    def test_follow_update_tape(self):
        """Check a new post's location."""
        Follow.objects.create(author=self.post_author, user=self.user)
        Post.objects.create(
            text='Test_post_2',
            author=self.post_author,
        )
        page = reverse('posts:follow_index')
        cache.clear()
        response = self.clients['authorized'].get(page)
        page_obj = response.context['page_obj']
        self.assertIn(
            Post.objects.get(text='Test_post_2'),
            page_obj
        )
        cache.clear()
        response = self.auth_nonfollower.get(page)
        page_obj = response.context['page_obj']
        self.assertNotIn(
            Post.objects.get(text='Test_post_2'),
            page_obj
        )
