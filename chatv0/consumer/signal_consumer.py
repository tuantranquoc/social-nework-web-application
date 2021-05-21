from account.models import Profile
from community.models import Member, MemberInfo
from django.db.models import Q
import operator
from functools import reduce
import channels.layers
from django.dispatch import receiver
from post.models import Post
from notify.models import EntityType, Notification, NotificationChange, NotificationObject, SignalRoom, UserNotify
from django.db.models.signals import pre_save, post_save
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from channels.auth import login
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from ..models import Message, Room
from django.contrib.auth import get_user_model
from service.chat import chat_service
User = get_user_model()


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


def dest_message_to_json(message):
    if message:
        return {
            'author': message.author.username,
            'content': message.content,
            'created_at': str(message.created_at)
        }
