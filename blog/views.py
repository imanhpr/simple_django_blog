from typing import NewType

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from blog.models import Post

SlugType = NewType("SlugType", str)


def post_list(request: HttpRequest) -> HttpResponse:
    objects = Post.published_manager.all()
    print(len(objects))
    paginator = Paginator(object_list=objects, per_page=1)
    
    page_number = request.GET.get("page")
    try:
        posts = paginator.page(page_number)
        print(posts)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(
        request=request,
        template_name="blog/post/list.html",
        context={"page": posts},
    )


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: SlugType):
    post = get_object_or_404(
        Post,
        slug=post,
        status="published",
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, "blog/post/detail.html", {"post": post})
