from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save

User = get_user_model()


# Create your models here.
class Profile(models.Model):
    # 1 user 1 profile and 1 profile 1 user (goals)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    follower = models.ManyToManyField(User, related_name='following', blank=True)
    background = models.ImageField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatar', default='user.png')
    timestamp = models.DateTimeField(auto_now_add=True)  # time created
    updated = models.DateTimeField(auto_now=True)  # time update profile
    """
    profile_obj = Profile.objects.first() get all the user that following you
    follower = profile_obj.follower.all()

    following = user.following.all() get all the user that you follow
    user = Profile.objects.()
    """

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.user.username

    def __id__(self):
        return self.user.id

    def __time__(self):
        return self.timestamp

    def __point__(self):
        return self.user.positivepoint.point

    def __follower__(self):
        return self.follower.count()




class FollowerRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save, sender=User)
