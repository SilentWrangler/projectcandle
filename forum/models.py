from django.db import models

from precise_bbcode.fields import BBCodeTextField

from players.models import Player
# Create your models here.


class Post(models.Model):
    author = models.ForeignKey(Player, related_name = 'posts', on_delete = models.CASCADE)
    reply_to = models.ForeignKey('Post', blank=True, null=True, related_name = 'replies', on_delete = models.CASCADE)
    content = BBCodeTextField()
    headline = models.CharField(max_length = 124)
    categories = models.ManyToManyField('Category')
    post_time = models.DateTimeField(auto_now_add = True)
    last_edit_time = models.DateTimeField(auto_now = True)
    last_editor =  models.ForeignKey(Player,blank=True, null=True, on_delete = models.CASCADE)
    last_edit_reason = models.CharField(max_length = 124, blank = True)
    frontpage = models.BooleanField(default = False)


class Category(models.Model):
    name = models.CharField(max_length = 124, unique = True)
    subscribers = models.ManyToManyField(Player, related_name = 'subscriptions')


