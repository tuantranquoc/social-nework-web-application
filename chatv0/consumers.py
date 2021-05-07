import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message, Room
from django.contrib.auth import get_user_model
from service.chat import chat_service
User = get_user_model()
from channels.auth import login
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models.signals import pre_save, post_save
from notify.models import EntityType, Notification, NotificationChange, NotificationObject, SignalRoom, UserNotify
from post.models import Post
from django.dispatch import receiver
import channels.layers
from functools import reduce
import operator
from django.db.models import Q
from community.models import Member, MemberInfo
from account.models import Profile


class ChatConsumer(WebsocketConsumer):
    def fetch_message(self, data):
        messages = Message.last_10_messages()
        print("count message")
        content = {'messages': messages_to_json(messages)}
        self.send_chat_message(content)

    def new_message(self, data):
        author = data['from']
        room = Room.objects.filter(pk=self.room_name).first()
        print("author send the message", author)
        author_user = User.objects.filter(username=author).first()
        print("data", data['message'])
        message = Message.objects.create(author=author_user,
                                         content=data['message'],
                                         room=room)
        print("token", data['token'])
        print('new message in room', self.room_name)
        content = {
            'command': 'new_message',
            'message': message_to_json(message)
        }
        print("dest-user", self.room_name)
        print("author", author_user)
        dest_user = room.user.all()

        signal_room = SignalRoom.objects.filter(user=author_user).first()
        room_group_name = 'signal_%s' % signal_room.id
        print("message signal room", room_group_name)
        notify_message = "You have a new message from " + author
        message = {"message": notify_message, "type": "notification"}
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(room_group_name, {
            'type': 'signal_message',
            'message': message
        })
        return self.send_chat_message(content)

    def on_connect(self, data):
        print("token-on-connect", data['token'])
        token = data['token']
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        if user:
            room = Room.objects.filter(pk=self.room_name, user=user).first()
            messages = Message.objects.filter(room=room)[:10]
            last_ten_message = reversed(messages)
            if room:
                content = {
                    'messages': messages_to_json(last_ten_message),
                    'user': self.user.username
                }
                self.send_chat_message(content)

    def on_load_more(self, data):
        token = data['token']
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        page_size = data['page_size']
        print('on_load_more')
        if page_size:
            room = Room.objects.filter(pk=self.room_name, user=user).first()
            messages = Message.objects.filter(room=room)[:int(page_size)]
            last_ten_message = reversed(messages)
            if room:
                content = {
                    'messages': messages_to_json(last_ten_message),
                    'user': self.user.username
                }
                self.send_chat_message(content)

    command = {
        'fetch_message': fetch_message,
        'new_message': new_message,
        'on_connect': on_connect,
        'on_load_more': on_load_more
    }

    def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                                                    self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name,
                                                        self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.command[data['command']](self, data)
        print("mess rec")

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
        })

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    def signal_message(self, event):
        message = event['message']
        self.send_chat_message(message)


class SignalConsumer(WebsocketConsumer):
    def fetch_message(self, data):
        messages = Message.last_10_messages()
        print("count message")
        content = {'messages': messages_to_json(messages)}
        self.send_chat_message(content)

    def new_message(self, data):
        author = data['from']
        room = Room.objects.filter(pk=self.room_name).first()
        print("author send the message", author)
        author_user = User.objects.filter(username=author).first()
        print("data", data['message'])
        message = Message.objects.create(author=author_user,
                                         content=data['message'],
                                         room=room)
        print("token", data['token'])
        print('new message in room', self.room_name)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def on_connect(self, data):
        print("token-on-connect-signal", data['token'])
        token = data['token']
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        print("got user", user)
        if user:
            room = Room.objects.filter(pk=self.room_name, user=user).first()
            messages = Message.objects.filter(room=room)
            if room:
                content = {
                    'signal': "connected to open socket",
                    'user': user.username
                }
                self.send_chat_message(content)

    def on_signal(self, data):
        print('hello world aaa')

    command = {
        'fetch_message': fetch_message,
        'new_message': new_message,
        'on_connect': on_connect,
        'on_signal': on_signal
    }

    def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'signal_%s' % self.room_name
        print("connect to signal room", self.room_group_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                                                    self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name,
                                                        self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.command[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
        })

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))

    def signal_message(self, event):
        message = event['message']
        print('rec-mess', message)
        self.send_chat_message(message)


# @receiver(post_save, sender=Notification)
# def my_handler(sender, instance, **kwargs):
#     notify_message = instance.notification_object.entity_type.notify_message
#     notifycation_change = NotificationChange.objects.filter(
#         notification_object=instance.notification_object).first()
#     notify_message = notify_message.replace(
#         "User A", "User " + notifycation_change.user.username)

#     for u in instance.user_notify.all():
#         print(u.user.username)
#         signal_room = SignalRoom.objects.filter(user=u.user).first()
#         print("message", notify_message)
#         room_group_name = 'signal_%s' % signal_room.id
#         # room_group_name = 'signal_%s' % 4
#         print(room_group_name)
#         message = {"message": notify_message, "type": "notification"}

#         channel_layer = channels.layers.get_channel_layer()

#         async_to_sync(channel_layer.group_send)(room_group_name, {
#             'type': 'signal_message',
#             'message': message
#         })


# @receiver(pre_save, sender=Post)
# def post_create_handler(sender, instance, **kwargs):
#     community = instance.community
#     post = instance
#     user = instance.user
#     post_id = instance.id
#     print("post_id", post_id)
#     entity_type = EntityType.objects.filter(id=1).first()
#     notification_object = NotificationObject.objects.create(
#         entity_type=entity_type, post=post)
#     notifycation_change = NotificationChange.objects.create(
#         user=instance.user, notification_object=notification_object)
#     notification = Notification.objects.filter(community=community).first()
#     if notification:
#         print("hello world")
#     else:
#         print("create new one")
#         notification = Notification.objects.create(community=community)
#         member_info = MemberInfo.objects.filter(community=community)
#         member = Member.objects.filter(member_info__in=member_info)
#         profiles = Profile.objects.filter(
#             reduce(operator.or_, (Q(user=x.user) for x in member)))
#         for p in profiles:
#             user_notify = UserNotify.objects.create(user=p.user)
#             user_notify.notification_object.add(notification_object)
#             user_notify.save()
#             notification.user_notify.add(user_notify)
#         notification.save()


@receiver(post_save, sender=UserNotify)
def user_notify_create_handler(sender, instance, **kwargs):
    message = instance.message
    if message:
        print("message from notify",message)
        signal_room = SignalRoom.objects.filter(user=instance.user).first()
        room_group_name = 'signal_%s' % signal_room.id
        # room_group_name = 'signal_%s' % 4
        print(room_group_name)
        message = {"message": message, "type": "notification"}
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(room_group_name, {
            'type': 'signal_message',
            'message': message
        })



def messages_to_json(messages):
    result = []
    for message in messages:
        result.append(message_to_json(message))
    return result


def message_to_json(message):
    if message:
        return {
            'author': message.author.username,
            'content': message.content,
            'created_at': str(message.created_at)
        }
