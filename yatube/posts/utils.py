from django.conf import settings
from django.core.paginator import Paginator

from .models import Follow


def page_object(request, objects):
    paginator = Paginator(objects, settings.SHOWN_POSTS_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def is_follow(request, author) -> bool:
    return Follow.objects.filter(user=request.user, author=author).exists()
