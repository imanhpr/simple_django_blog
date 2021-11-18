from typing import NewType

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from blog.models import Post

SlugType = NewType("SlugType", str)


def post_list(request: HttpRequest) -> HttpResponse:
    posts = Post.published.all()
    return render(
        request=request, template_name="blog/post/list.html", context={"posts": posts}
    )


def post_detail(request: HttpRequest, year: int, month: int, day: int, post : SlugType):
    post = get_object_or_404(
        Post,
        slug=post,
        status="published",
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, "blog/post/detail.html", {"post": post})
