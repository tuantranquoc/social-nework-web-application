from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Community(models.Model):
    id = models.AutoField(primary_key=True)
    community_type = models.CharField(max_length=255, blank=True, null=True)
    user = models.ManyToManyField(User, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="owner")
    state = models.BooleanField(default=True)
    description = models.TextField(default="")
    avatar = models.ImageField(upload_to='images/', blank=True, null=True)
    background = models.ImageField(upload_to='images/', blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.community_type

    def __user_count__(self):
        return self.user.count()

    def __id__(self):
        return self.id

    def __timestamp__(self):
        return self.time_stamp

    def __creator__(self):
        return self.creator

    def __state__(self):
        return self.state

    def __description__(self):
        return self.description
