from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.generic.list import ListView

from .forms import PostForm, ReplyForm, NonAdminPostForm, NonAdminReply
from .models import Post, Category

# Create your views here.


@login_required
def make_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)  if request.user.is_staff else NonAdminPostForm(request.POST)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                post.author = request.user
                post.frontpage = form.data.get('frontpage', False) #Для неадминской формы
                post.last_edit_reason = form.data.get('last_edit_reason', '')
                assert not post.frontpage or request.user.is_staff, "Frontpage posts are admin restricted"
                post.save()
                return redirect('showpost', pk = post.id)
            except AssertionError:
                form.add_error(None, "Frontpage posts are admin restricted")
    else:
        form = PostForm()  if request.user.is_staff else NonAdminPostForm()

    return render(request, 'makepost.html', {'form': form})

@login_required
def make_reply(request, pk):
    OP = get_object_or_404(Post, pk = pk)
    if request.method == 'POST':
        form = PostForm(request.POST) if request.user.is_staff else NonAdminPostForm(request.POST)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                post.author = request.user
                post.frontpage = form.data.get('frontpage', False) #Для неадминской формы
                post.last_edit_reason = form.data.get('last_edit_reason', '')
                assert ( not post.frontpage ) or request.user.is_staff, "Frontpage posts are admin restricted"
                post.save()
                return redirect('showpost',  pk = pk) #When replying, show original
            except AssertionError:
                form.add_error(None, "Frontpage posts are admin restricted")
    else:
        form = ReplyForm(OP) if request.user.is_staff else NonAdminReply(OP)

    return render(request, 'makepost.html', {'form': form, 'OP':OP})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk = pk)
    if request.method == 'POST':
        form = PostForm(request.POST, instance = post)
        if form.is_valid():
            try:
                post = form.save(commit = False)
                assert not post.frontpage or request.user.is_staff, "Frontpage posts are admin restricted"
                assert request.user == post.author or request.user.is_staff, "Only author or admin can edit this post"
                post.save()
                return redirect('showpost', id = post.id)
            except AssertionError as err:
                form.add_error(None, err.args[0])
    else:
        form = PostForm(instance = post) if request.user.is_staff else NonAdminPostForm(instance = post)

    return render(request, 'makepost.html', {'form': form})

def view_post(request, pk):
    post = get_object_or_404(Post, pk = pk)
    form = None
    if request.user.is_authenticated:
        form = NonAdminReply(post)
    return render(request, 'showpost.html', {'post': post, 'form':form})



class Categories(ListView):
    model = Category
    template = 'category_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def category(request, pk):
    cat = get_object_or_404(Category, pk = pk)
    posts = Post.objects.filter(categories__in=[cat], reply_to__isnull=True).order_by('-post_time')
    return render(request, 'showcat.html', {'cat': cat, 'posts':posts })

