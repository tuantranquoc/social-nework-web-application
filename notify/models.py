from django.db import models
from post.models import Post, Comment
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save

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


class EntityType(models.Model):
    description = models.TextField(blank=True, null=True)
    notify_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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


class Notification(models.Model):
    user = models.ManyToManyField(
        User,
        blank=True,
    )
    status = models.IntegerField(default=0)
    notification_object = models.ForeignKey(NotificationObject,
                                            on_delete=models.CASCADE,
                                            blank=True,
                                            null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)


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


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        SignalRoom.objects.get_or_create(user=instance)


# user save will trigger profile save
post_save.connect(user_did_save, sender=User)