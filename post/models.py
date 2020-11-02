from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db.models.signals import post_save, pre_save
from community.models import Community

User = get_user_model()


# Create your models here.


class Post(models.Model):
    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    up_vote = models.ManyToManyField(User, related_name="p_up_vote", blank=True)
    down_vote = models.ManyToManyField(User, related_name="p_down_vote", blank=True)
    image = models.FileField(upload_to='images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=60, blank=True, null=True)
    type = models.OneToOneField("PostType", blank=True, null=True, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=0)

    # view = models.ForeignKey("View", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def __id__(self):
        return self.id

    def __str__(self):
        return self.title or "NO_TITLE"

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


class PositivePoint(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
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
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    up_vote = models.ManyToManyField(User, related_name="c_up_vote", blank=True)
    down_vote = models.ManyToManyField(User, related_name="c_down_vote", blank=True)

    def __id__(self):
        return self.id

    def __str__(self):
        return self.content or "@!$"

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


class PostType(models.Model):
    type = models.CharField(max_length=60)

    def __str__(self):
        return self.type


class View(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ManyToManyField(User)
    old_timestamp = models.DateTimeField(blank=True, null=True, default=None)

    def __user__(self):
        return self.user

    def __old_timestamp__(self):
        return self.old_timestamp




def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        View.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save, sender=User)
