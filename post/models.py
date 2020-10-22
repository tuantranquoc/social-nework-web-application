from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

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

    class Meta:
        ordering = ['-id']

    def __id__(self):
        return self.id

    def __str__(self):
        return self.content or "@!$"

    def __time__(self):
        return self.timestamp

    def __up_vote__(self):
        return self.up_vote.count()

    def __down_vote__(self):
        return self.down_vote.count()


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


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        PositivePoint.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save, sender=User)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
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
        return self.parent.id

    def __post__(self):
        return self.post.id

    def __up_vote__(self):
        return self.up_vote.count()

    def __down_vote__(self):
        return self.down_vote.count()