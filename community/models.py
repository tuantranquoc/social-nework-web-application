from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import truncatechars
from django.db.models.signals import post_save
User = get_user_model()


# Create your models here.
class Community(models.Model):
    id = models.AutoField(primary_key=True)
    community_type = models.CharField(max_length=255, blank=True, null=True)
    user = models.ManyToManyField(User, blank=True)
    parent = models.ForeignKey("self",
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                                related_name="owner")
    state = models.BooleanField(default=True)
    description = models.TextField(default="")
    avatar = models.ImageField(upload_to='images/', blank=True, null=True)
    background = models.ImageField(upload_to='images/', blank=True, null=True)
    rule = models.TextField(blank=True, null=True)
    background_color = models.CharField(default='#30363C', max_length=7)
    title_background_color = models.CharField(default='#f5c007', max_length=7)
    description_background_color = models.CharField(default='#ffffff',
                                                    max_length=7)
    button_background_color = models.CharField(default='#d7dadc', max_length=7)
    button_text_color = models.CharField(default='#1a1a1b', max_length=7)
    text_color = models.CharField(default='#000000', max_length=7)
    post_background_color = models.CharField(default='#ffffff', max_length=7)
    mod = models.ManyToManyField(User, blank=True, related_name='mod')

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
        return truncatechars(self.description, 20)

    def __rule__(self):
        return self.rule

    def __color__(self):
        return self.background_color

    def __mod__(self):
        return ",".join(
            [str(p.username) for p in self.mod.all().order_by('-id')])


class MemberInfo(models.Model):
    community = models.ForeignKey(Community,
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    state = models.BooleanField(default=True)
    role = models.CharField(max_length=30, default='MEMBER')

    def __id__(self):
        return self.id

    def __community__(self):
        return self.community.community_type

    def __timestamp__(self):
        return self.timestamp

    def __state__(self):
        return self.state

    def __role__(self):
        return self.role


class Member(models.Model):
    user = models.OneToOneField(User,
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)
    member_info = models.ManyToManyField(MemberInfo, blank=True)

    def __user__(self):
        return self.user.username

    # def __community__(self):
    #     return ",".join([
    #         str(p.community.community_type)
    #         for p in self.member_info.all().order_by('-timestamp')
    #     ])

    def __community__(self):
        return ",".join([
            str(p.community.community_type)
            for p in self.member_info.filter(state=True).order_by('-timestamp')
        ])

    def __id__(self):
        return self.id


def user_did_save(sender, instance, created, *args, **kwargs):
    if created:
        Member.objects.get_or_create(user=instance)


post_save.connect(user_did_save, sender=User)


class CommunityHistory(models.Model):
    community = models.ForeignKey(Community,
                                  null=True,
                                  blank=True,
                                  on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    target = models.ForeignKey(User,
                               blank=True,
                               null=True,
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='community_history_user')
    old_role = models.CharField(default='MEMBER', max_length=20)
    new_role = models.CharField(default='MEMBER', max_length=20)

    class Meta:
        ordering = ['-timestamp']

    def __id__(self):
        return self.id

    def __line__(self):
        return self.line

    def __community__(self):
        return self.community

    def __timestamp__(self):
        return self.timestamp

    def __change_by__(self):
        return self.user.username

    def __old_role__(self):
        return self.old_role

    def __new_role__(self):
        return self.new_role

    def __target__(self):
        return self.target


class BlackListType(models.Model):
    type = models.CharField(max_length=25, default='VIEW_ONLY')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type

    def __description__(self):
        return self.description


class CommunityBlackListDetail(models.Model):
    user = models.ManyToManyField(User, blank=True)
    blacklist_type = models.ForeignKey(BlackListType,
                                       blank=True,
                                       on_delete=models.CASCADE,
                                       null=True)
    from_timestamp = models.DateTimeField(auto_now_add=True,
                                          null=True,
                                          blank=True)
    to_timestamp = models.DateTimeField(blank=True, null=True)

    def __from_timestamp__(self):
        return self.from_timestamp

    def __to_timestamp__(self):
        return self.timestamp


class CommunityBlackList(models.Model):
    community = models.ForeignKey(Community,
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE)
    blacklist_detail = models.OneToOneField(CommunityBlackListDetail,
                                            blank=True,
                                            null=True,
                                            on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    def __community__(self):
        return self.community.community_type

    def __user__(self):
        if self.blacklist_detail:
            return ",".join(
                [str(p.username) for p in self.blacklist_detail.user.all()])
        return None


def save_blacklist(sender, instance, created, *args, **kwargs):
    if created:
        CommunityBlackList.objects.get_or_create(community=instance)


post_save.connect(save_blacklist, sender=Community)