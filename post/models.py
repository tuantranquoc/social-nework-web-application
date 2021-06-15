from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from community.models import Community
from post import choice

User = get_user_model()


# Create your models here.




class Post(models.Model):
    parent = models.ForeignKey("self",
                               null=True,
                               on_delete=models.SET_NULL,
                               blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.TextField(blank=True, null=True)
    up_vote = models.ManyToManyField(User,
                                     related_name="p_up_vote",
                                     blank=True)
    down_vote = models.ManyToManyField(User,
                                       related_name="p_down_vote",
                                       blank=True)
    image = models.FileField(upload_to='images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey(Community,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey("PostType",
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)
    point = models.FloatField(default=0)
    state = models.CharField(max_length=10,
                             blank=False,
                             null=True,
                             default='public')
    hidden = models.BooleanField(default=False)
    hidden_in_community= models.BooleanField(default=False)
    # vote = models.ManyToManyField(UserVote, blank=True)

    class Meta:
        ordering = ['-point']

    def __id__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def __time__(self):
        return self.timestamp

    def __up_vote__(self):
        return self.up_vote.count()

    def __down_vote__(self):
        return self.down_vote.count()

    def __type__(self):
        if self.type:
            return self.type.type
        return None

    def __title__(self):
        return self.title

    def __view__(self):
        return self.view_count

    def __user__(self):
        return self.user.username

    def __point__(self):
        return self.point

    def __community__(self):
        return self.community

    def __state__(self):
        return self.state

    # def hidden(self):
    #     return self.hidden


class UserVote(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    down_vote = models.IntegerField(choices=choice.STATUS_CHOICES, default=0)
    dislike = models.IntegerField(choices=choice.STATUS_CHOICES, default=0)
    view = models.IntegerField(choices=choice.STATUS_CHOICES, default=0)
    like = models.IntegerField(choices=choice.STATUS_CHOICES, default=0)
    share = models.IntegerField(choices=choice.STATUS_CHOICES, default=0)

    def __str__(self):
        # return ("User ratting" + " "  + self.user.username)
        return ("Vote id" + " " + str(self.id) + " " + self.user.username)

    def get_rating(self):
        return 2 + self.view + self.like + self.share - self.dislike - self.down_vote



class PositivePoint(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User,
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)
    point = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def __point__(self):
        return self.point

    def __id__(self):
        return self.id


def user_did_save_pp(sender, instance, created, *args, **kwargs):
    if created:
        PositivePoint.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save_pp, sender=User)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self',
                               null=True,
                               on_delete=models.CASCADE,
                               blank=True)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    up_vote = models.ManyToManyField(User,
                                     related_name="c_up_vote",
                                     blank=True)
    down_vote = models.ManyToManyField(User,
                                       related_name="c_down_vote",
                                       blank=True)
    point = models.FloatField(default=0)
    level = models.IntegerField(default=1)
    state = models.CharField(blank=False,
                             null=True,
                             max_length=10,
                             default='public')

    class Meta:
        ordering = ['-point']

    def __id__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def __timestamp__(self):
        return self.timestamp

    def __user__(self):
        return self.user.username

    def __parent__(self):
        if self.parent:
            return self.parent.id
        return None

    def __post__(self):
        if self.post:
            return self.post.id

    def __up_vote__(self):
        return self.up_vote.count()

    def __down_vote__(self):
        return self.down_vote.count()

    def __point__(self):
        return self.point

    def __level__(self):
        return self.level

    def __parent__(self):
        if self.parent:
            return self.parent.id
        return None

    def __state__(self):
        return self.state


class CommentPoint(models.Model):
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)
    point = models.FloatField(default=0)

    class Meta:
        ordering = ['-point']

    def __id__(self):
        return self.comment.id

    def __point__(self):
        return self.point


class PostType(models.Model):
    type = models.CharField(max_length=60)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.type


class View(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    user = models.ManyToManyField(User)
    old_timestamp = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        ordering = ['-id']

    def __user__(self):
        return self.user.count()

    def __old_timestamp__(self):
        return self.old_timestamp



