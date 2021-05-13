from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.urls import reverse
from django.template.defaultfilters import slugify


STATUS = (('FOR SALE', 'For Sale'), ('FOR RENT', 'For Rent'))


class Post(models.Model):
    status = models.CharField(max_length=10, choices=STATUS)
    price = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    
    tags = TaggableManager()
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="blog_posts")

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.address

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.post.address, self.name)


def get_image_filename(instance, filename):
    title = instance.post.address
    slug = slugify(title)
    return "post_images/%s-%s" % (slug, filename) 


class PostImage(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    image = models.FileField(upload_to=get_image_filename, verbose_name='Image')

    def __str__(self):
        return self.post.title
