from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

STATUS = (('FOR SALE', 'For Sale'), ('FOR RENT', 'For Rent'))

class Post(models.Model):
    status = models.CharField(max_length=10, choices=STATUS)
    price = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    # create foreign key from post to user
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.address

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})
    