from django.shortcuts import render, redirect, get_object_or_404

from .forms import PostForm, ReplyForm
from .models import Post

# Create your views here.

def make_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                assert not post.frontpage or request.user.is_staff, "Frontpage posts are admin restricted"
                post.save()
                return redirect('post', id = post.id)
            except AssertionError:
                form.add_error(None, "Frontpage posts are admin restricted")
    else:
        form = PostForm()

    return render(request, 'makepost.html', {'form': form})


def make_reply(request, pk):
    OP = get_object_or_404(Post, pk = pk)
    if request.method == 'POST':
        form = ReplyForm(OP,request.POST)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                assert not post.frontpage or request.user.is_staff, "Frontpage posts are admin restricted"
                post.save()
                return redirect('post', id = post.id)
            except AssertionError:
                form.add_error(None, "Frontpage posts are admin restricted")
    else:
        form = ReplyForm(OP)

    return render(request, 'makepost.html', {'form': form, 'OP':OP})

def edit_post(request, pk):
    post = get_object_or_404(Post, pk = pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance = post)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                assert not post.frontpage or request.user.is_staff, "Frontpage posts are admin restricted"
                post.save()
                return redirect('post', id = post.id)
            except AssertionError:
                form.add_error(None, "Frontpage posts are admin restricted")
    else:
        form = PostForm(instance = post)

    return render(request, 'makepost.html', {'form': form})

def view_post(request, pk):
    post = get_object_or_404(Post, pk = pk)
    return render(request, 'showpost.html', {'post': post})





