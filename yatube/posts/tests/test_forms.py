import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from .conf import IMAGE, TestConfig
from ..forms import PostForm
from ..models import Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestConfig):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.group = Group.objects.get(id=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_create_post(self):
        """Valid form creates a post."""
        posts_count = Post.objects.count()
        small_gif = IMAGE
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст нового поста',
            'group': PostFormTests.group.id,
            'image': uploaded
        }
        client = self.clients['authorized']
        user = self.users[client]
        response = client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': user}
            )
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Incorrect posts amount'
        )
        self.assertTrue(
            Post.objects.select_related('author').filter(
                text=form_data['text'],
                author__username=user,
                group=PostFormTests.group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Valid form edits a post."""
        form_data = {
            'text': 'Измененный текст',
        }
        client = self.clients['author']
        user = self.users[client]
        post = Post.objects.select_related('author').filter(
            author__username=user
        )[0]
        response = client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id}
            )
        )
        self.assertTrue(
            Post.objects.select_related('author').filter(
                id=post.id,
                text=form_data['text'],
                author__username=user,
                group__isnull=True
            ).exists()
        )
