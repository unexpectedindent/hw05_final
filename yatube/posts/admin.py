from django.contrib import admin

from .models import Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Allows to show and edit post's parametrs.
    Displayed fields: post's id, text, date, author, group.
    Editable fields: group.
    Available search by: text.
    Available filter by: date of publication.
    """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Allows to show and edit group's parametrs.
    Displayed fields: group's id, title, description, path.
    Editable fields: title, description.
    Available search by: description.
    Available filter by: title.
    """
    list_display = ('pk', 'title', 'description', 'slug',)
    list_editable = ('title', 'description',)
    search_fields = ('description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'
    ordering = ('pk',)
