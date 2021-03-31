import channels.layers
from asgiref.sync import async_to_sync

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Notification
import json

# @receiver(pre_save, sender=Notification)
# def my_handler(sender, instance, **kwargs):
#     room_group_name = 'chat_%s' % "9"
#     print(room_group_name)
#     print("hello world", instance.user, instance.notification_object)
#     message = {"message":"notification created","username": str(instance.user.username),"type":"notification"}

#     channel_layer = channels.layers.get_channel_layer()

#     async_to_sync(channel_layer.group_send)(room_group_name, {
#         'type': 'signal_message',
#         'message': message
#     })
