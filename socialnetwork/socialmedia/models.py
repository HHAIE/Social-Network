from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.html import mark_safe
from .tasks import *
from django.db.models import Q

# Users table
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthDate = models.DateField(
        null=False, blank=True, default=datetime.date(1970, 1, 1))
    friends = models.ManyToManyField('self',
                                     blank=True, through='UserUserFriend')

    def __unicode__(self):
        return self.user.username

    # method to return a list of the current user friends
    def getFriends(self):
        return self.friends.through.objects.filter(Q(user1=self) | Q(user2=self)).distinct()

    def __str__(self):
        return self.user.username

# Images table
class Image(models.Model):
    name = models.CharField(max_length=256, unique=True, db_index=True)
    image = models.ImageField(upload_to='')
    thumbnail = models.ImageField(null=True)
    user = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="images")

    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)
        
        # After adding a new image, create a thumbnail for it
        if not self.thumbnail:
            make_thumbnail.delay(self.pk)

    def __str__(self):
        return self.name

    # Method to return a small view of the current image
    def image_tag(self):
        return mark_safe('<img src="/images/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'

# Posts table
class Status(models.Model):
    status = models.CharField(max_length=250, null=False)

    # Creation date
    date = models.DateTimeField(auto_now_add=True)

    # Last modification date
    lastDate = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="statuses")

    def __str__(self):
        return self.status


class UserUserFriend(models.Model):
    user1 = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="friend_user1")
    user2 = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, related_name="friend_user2")
    date = models.DateTimeField(auto_now_add=True)
    chat = models.TextField(null=False, blank=True)

