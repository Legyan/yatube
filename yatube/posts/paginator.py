from django.conf import settings
from django.core.paginator import Paginator


def post_paginator(request, post_list):
    """Пагинация постов."""
    paginator = Paginator(post_list, settings.LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
