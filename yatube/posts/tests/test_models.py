from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост длиной более 15 сиволов',
        )
        cls.link = Follow.objects.create(
            author=cls.author,
            user=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Comment_text_text_text'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        objects_as_string = {
            post: 'Тестовый пост д',
            group: 'Тестовая группа',
            comment: 'Comment_text_te'
        }
        for model, model_obj_as_str in objects_as_string.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model),
                    model_obj_as_str,
                    ('Неверно работает метод str в модели'
                     f' {model.__class__.__name__}')
                )

    def test_models_verbose_names(self):
        """Проверяем отображаемые заголовки полей."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        link = PostModelTest.link
        field_verb_name = {
            post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Сообщество',
                'image': 'Картинка'
            },
            group: {
                'title': 'Название',
                'slug': 'Ссылка',
                'description': 'Описание',
            },
            comment: {
                'post': 'Комментарий',
                'author': 'Автор',
                'text': 'Текст сообщения'
            },
            link: {
                'user': 'Подписчик',
                'author': 'Автор'
            }
        }
        for model in field_verb_name:
            for field, field_verbose_name in field_verb_name[model].items():
                with self.subTest():
                    self.assertEqual(
                        model._meta.get_field(field).verbose_name,
                        field_verbose_name,
                        (f'Отображаемое имя поля {field} модели '
                         f'{model.__class__.__name__} '
                         'не соответствует ожидаемому.'
                         )
                    )

    def test_models_help_text(self):
        """Проверяем пояснительный текст для полей моделей."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        field_help_text = {
            post: {
                'text': 'Текст нового поста',
                'group': 'Группа, к которой будет относиться пост',
                'image': 'Выберете файл с изображением'
            },
            group: {
                'title': 'Заголовок группы',
                'slug': ('Адрес страницы группы. Используйте только '
                         'латиницу, цифры, дефисы и знаки подчёркивания'),
                'description': 'Краткое описание сообщества',
            },
            comment: {
                'text': 'Введите текст Вашего сообщения'
            }
        }
        for model in field_help_text:
            for field, help_text in field_help_text[model].items():
                with self.subTest():
                    self.assertEqual(
                        model._meta.get_field(field).help_text,
                        help_text,
                        (f'Вспомогательный текст для поля {field} '
                         f'модели {model.__class__.__name__} '
                         'не соответствует ожидаемому.'
                         )
                    )
