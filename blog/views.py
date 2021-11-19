from typing import NewType

from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse

from blog.forms import CommentForm, EmailPostForm
from blog.models import Comment, Post

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
        context={"posts": posts},
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
    comments = post.comments.filter(active=True)
    if request.method == "POST":
        comments_form = CommentForm(data=request.POST)
        if comments_form.is_valid():
            new_comment = comments_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            messages.success(request, message="Your Comment Add!")
            return redirect(post)
    else:
        comments_form = CommentForm()
    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_form": comments_form,
        },
    )


def post_share(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id, status="published")

    if request.method == "POST":
        form = EmailPostForm(data=request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{clean_data['name']} recommends you read {post.title}"
            message = f"""
            Read {post.title} at { post_url }\n\n{clean_data['name']}'s comments: {clean_data['comments']}
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=clean_data["email"],
                recipient_list=[clean_data["to"]],
            )
            success_message = f"post : {post.title} send from {clean_data['email']} to {clean_data['to']}"
            messages.success(request, message=success_message)
            return redirect(
                reverse(
                    "blog:post_detail",
                    kwargs={
                        "year": post.publish.year,
                        "month": post.publish.month,
                        "day": post.publish.day,
                        "post": post.slug,
                    },
                )
            )
        else:
            print(form.errors)
    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {
            "post": post,
            "form": form,
        },
    )
