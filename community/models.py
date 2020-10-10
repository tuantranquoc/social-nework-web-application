from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Community(models.Model):
    id = models.AutoField(primary_key=True)
    community_type = models.CharField(max_length=255, blank=True, null=True)
    user = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.community_type

    def __count__(self):
        return self.post.count()

    def __user_count__(self):
        return self.count()

    def __id__(self):
        return self.id


class SubCommunity(models.Model):
    id = models.AutoField(primary_key=True)
    community_type = models.CharField(max_length=255, null=True)
    parent = models.ForeignKey(Community, on_delete=models.CASCADE, null=True)
    sub_parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.community_type

    def __id__(self):
        return self.id

    def __count__(self):
        return self.post.count()

    def __parent__(self):
        return self.parent

    def __sub_parent__(self):
        return self.sub_parent

    def __timestamp__(self):
        return self.time_stamp
