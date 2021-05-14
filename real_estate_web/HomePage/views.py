from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from .models import Post, Comment, PostImage
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.shortcuts import render, reverse
from taggit.models import Tag
from .models import *


class TagMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TagMixin, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context


class PostListView(TagMixin, ListView):
    model = Post
    template_name = 'HomePage/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 3
    def get_queryset(self):
        search_post = self.request.GET.get('search')
        if search_post:
            posts = Post.objects.filter(Q(address__icontains=search_post) | Q(description__icontains=search_post))
        else:
            posts = Post.objects.all()
        return posts.order_by('-date_posted')


class TagIndexView(TagMixin, ListView):
    model = Post
    template_name = 'HomePage/tag_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 3
    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get('tag_slug'))


class UserPostListView(TagMixin, ListView):
    model = Post
    template_name = 'HomePage/user_posts.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 3

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(TagMixin, DetailView):
    model = Post
    def get_context_data(self, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)

        stuff = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = stuff.total_likes()

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked = True
        
        context["photos"]= PostImage.objects.filter(post=stuff)
        context["total_likes"] = total_likes
        context["liked"] = liked
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['status', 'price', 'address', 'description', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['status', 'price', 'address', 'description', 'tags']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    success_url = '/'
    fields = ['name', 'body']

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)


def about(request):
    return render(request, 'HomePage/about.html', {'title': 'About'})


def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['status', 'price', 'address', 'description', 'tags']


class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields= ('image',)
        widgets = {
            'image': forms.FileInput(attrs={'multiple':True,}),
        }


@login_required
def create_new_post(request):
    ImageFormSet = modelformset_factory(PostImage, form=PostImageForm, extra=10)
    #'extra' means the number of photos that you can upload
    if request.method == 'POST':
        form = PostForm(request.POST)
        formset =  ImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
        if form.is_valid() and formset.is_valid():
            post_form = form.save(commit=False)
            post_form.author = request.user
            post_form.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = PostImage(post=post_form, image=image)
                    photo.save()
            messages.success(request, "Success, check it out on the home page!")
            return HttpResponseRedirect("/")
        else:
            print(form.errors, formset.errors)
    else:
        form = PostForm()
        formset = ImageFormSet(queryset=PostImage.objects.none())
    
    context = {
        'form': form, 
        'formset': formset,
    }

    return render(request, 'HomePage/post_form.html', context)