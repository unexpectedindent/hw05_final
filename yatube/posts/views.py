from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import is_follow, page_object


@cache_page(5)
def index(request):
    """Returns main page."""
    posts = Post.objects.all()
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_object(request, posts)}
    )


def group_posts(request, slug):
    """Returns the posts of selected group."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': page_object(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Returns page with posts of selected author."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'author': author,
        'page_obj': page_object(request, posts),
        'following': is_follow(request, author),
    }
    return render(request, 'posts/profile.html', context)


@cache_page(20)
def post_detail(request, post_id):
    """Returns page with selected post's details."""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.GET)
    return render(
        request,
        'posts/post_detail.html',
        {'post': post, 'form': form, 'comments': comments}
    )


@login_required
def post_create(request):
    """Returns page for creation a new post."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


@login_required
def post_edit(request, post_id):
    """
    Allows to edit post's (text and/or group) to its author.
    Returns edited post.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form}
    )


@login_required
def delete_post(request, post_id):
    """Deletes post if user is post's author."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    post.delete()
    return redirect('posts:profile', request.user.username)


@login_required
def add_comment(request, post_id):
    """Adds comment to post's object."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Fills page with posts of followed authors."""
    posts = Post.objects.filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {'page_obj': page_object(request, posts)}
    )


@login_required
def profile_follow(request, username):
    """Follow to the author."""
    author = get_object_or_404(User, username=username)
    if request.user != author and not is_follow(request, author):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Unfollow from the author."""
    author = get_object_or_404(User, username=username)
    if request.user != author and is_follow(request, author):
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
