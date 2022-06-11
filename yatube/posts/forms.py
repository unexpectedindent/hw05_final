from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """
    Creates an input form to new post.
    Allowed fields: text (required), group (optional), image (optional).
    """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """
    Creates an input form to new post.
    Allowed fields: text (required).
    """
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }
