from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm, CommentForm
from .models import Post, Group, Comment, User, Follow
from .paginator import post_paginator


def index(request):
    """Главная страница."""
    template = 'posts/index.html'
    post_list = Post.objects.select_related('group', 'author')
    page_obj = post_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group', 'author')
    page_obj = post_paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    """Страница с постами пользователя."""
    follower = request.user
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group', 'author')
    page_obj = post_paginator(request, post_list)
    following = False
    if follower.is_authenticated:
        following = Follow.objects.filter(
            user=follower, author=author).exists()
    context = {'page_obj': page_obj,
               'author': author,
               'following': following}
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница с подробной информацией о посте."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.select_related(
        'group',
        'author').filter(author=post.author).count()
    form = CommentForm(request.POST or None)
    comments_list = Comment.objects.filter(post_id=post_id)
    context = {'post': post,
               'count': count,
               'form': form,
               'comments': comments_list}
    return render(request, template, context)


@login_required
def post_create(request):
    """Страница создания поста."""
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            username = request.user
            form.cleaned_data['author'] = username
            Post.objects.create(**form.cleaned_data)
            return redirect('posts:profile', username)
    form = PostForm()
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = get_object_or_404(Post, pk=post_id)
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.image = form.cleaned_data['image']
            post.save()
            return redirect('posts:post_detail', post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(initial={'text': post.text, 'group': post.group})
    form.text = post.text
    context = {'form': form,
               'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Страница с комментированием поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = post_paginator(request, posts_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    follower = request.user
    author = User.objects.get(username=username)
    follow_exist = Follow.objects.filter(
        user=follower, author=author).exists()
    if not follow_exist and follower != author:
        Follow.objects.create(user=follower, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    author = User.objects.get(username=username)
    get_object_or_404(Follow,
                      user=follower,
                      author__username=username).delete()
    return redirect('posts:profile', username=author)
