from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel


User = get_user_model()


class Post(models.Model):
    """
    Post's object on the site.
    It contains next fields: id, author, text, date of publication, group.
    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Выберете файл с изображением'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        """Returns title of class's object."""
        return self.text[:settings.POST_TITLE_LEN]


class Group(models.Model):
    """
    Group's object on the site.
    It contains next fields: id, title, link (slug), description.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Заголовок группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка',
        help_text=('Адрес страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания')
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Краткое описание сообщества'
    )

    class Meta:
        ordering = ['pk']

    def __str__(self):
        """Returns title of class's object."""
        return self.title


class Comment(CreatedModel):
    """
    Comment's object on the site.
    It contains next fields: id, author, text, date of publication.
    Related with post's object and user's model.
    """
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комметарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Введите текст Вашего сообщения'
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        """Returns title of class's object."""
        return self.text[:settings.POST_TITLE_LEN]


class Follow(models.Model):
    """."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
