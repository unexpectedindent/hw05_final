from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Adds creation's date."""
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True
