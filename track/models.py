from django.db import models
from django.contrib.auth import get_user_model
from community.models import Community
from django.db.models import Count

User = get_user_model()


# Create your models here.
class CommunityTrack(models.Model):
    community = models.ForeignKey(Community,
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __id__(self):
        return self.id

    def __community__(self):
        return self.community.community_type

    def __timestamp__(self):
        return self.timestamp


class Track(models.Model):
    community_track = models.ManyToManyField(
        CommunityTrack,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(User,
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)

    def __user__(self):
        return self.user.username

    def __community__(self):
        return ",".join([
            str(p.community.community_type)
            for p in self.community_track.all().order_by('-timestamp')
        ])

    def __id__(self):
        return self.id
