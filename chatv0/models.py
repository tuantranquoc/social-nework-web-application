from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Room(models.Model):
    user = models.ManyToManyField(User, blank=True)
    room_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "room_id " + str(self.id)


class Message(models.Model):
    author = models.ForeignKey(User,
                               related_name='author_messages',
                               on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    room = models.ForeignKey(Room,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True)

    def __str__(self):
        return self.author.username

    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]
