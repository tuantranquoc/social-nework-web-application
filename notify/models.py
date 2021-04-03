from django.db import models
from post.models import Post, Comment
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from post.models import Community

User = get_user_model()


# Create your models here.
class SignalRoom(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True)

    def __id__(self):
        return self.id

    def str(self):
        return self.user.username



    

class CommunityNotify(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    status = models.IntegerField(default=0)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True, blank=True)
    message = models.TextField(blank=True)

    def __id__(self):
        return self.id
    


class EntityType(models.Model):
    description = models.TextField(blank=True, null=True)
    notify_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    def __id__(self):
        return self.id

    class Meta:
        ordering = [
            'id',
        ]


class NotificationObject(models.Model):
    entity_type = models.ForeignKey(EntityType,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=0)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)

    def __id__(self):
        return self.id


class UserNotify(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)
    notification_object = models.ManyToManyField(NotificationObject, blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, blank=True, null=True)


    def __id__(self):
        return self.id

    def username(self):
        return self.user.username



class Notification(models.Model):
    user_notify = models.ManyToManyField(
        UserNotify,
        blank=True,
    )
    # notification_object = models.ForeignKey(NotificationObject,
    #                                         on_delete=models.CASCADE,
    #                                         blank=True,
    #                                         null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True, null=True)

    def __id__(self):
        return self.id


class NotificationChange(models.Model):
    notification_object = models.ForeignKey(NotificationObject,
                                            on_delete=models.CASCADE,
                                            blank=True,
                                            null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    def __id__(self):
        return self.id


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        SignalRoom.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save, sender=User)