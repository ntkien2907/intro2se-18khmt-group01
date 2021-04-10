from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static 
from .views import (
    PostListView, 
    PostDetailView, 
    PostUpdateView, 
    PostDeleteView, 
    UserPostListView, 
    CommentCreateView, 
    LikeView
)
from . import views


urlpatterns = [
    path('', PostListView.as_view(), name='home-page'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', views.create_new_post, name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='home-about'),
    path('like/<int:pk>', LikeView, name='post-like'),
    path('post/<int:pk>/comment/', CommentCreateView.as_view(), name='comment-add'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)