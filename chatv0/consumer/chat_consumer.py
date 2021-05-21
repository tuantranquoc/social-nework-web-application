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
import random
import libnum
User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def fetch_message(self, data):
        messages = Message.last_10_messages()
        print("count message")
        content = {'messages': messages_to_json(messages)}
        return self.send_chat_message(content)

    def new_message(self, event):
        message = event['message']
        self.send_chat_message(message)
        print("sending", message)
        # dest = data['to']
        # room = Room.objects.filter(pk=self.room_name).first()
        # dest_user = User.objects.filter(username=dest).first()
        # author_user = room.user.filter(~Q(username=dest)).first()
        # message = Message.objects.create(author=author_user,
        #                                  content=data['message'],
        #                                  room=room)
        # content = {
        #     'command': 'new_message',
        #     'message': dest_message_to_json(message)
        # }
        # signal_room = SignalRoom.objects.filter(user=dest_user).first()
        # room_group_name = 'signal_%s' % signal_room.id

        # # notify_message = "You have a new message from " + author_user.username
        # message = {"message": message_to_json(message), "type": "message"}
        # channel_layer = channels.layers.get_channel_layer()
        # async_to_sync(channel_layer.group_send)(room_group_name, {
        #     'type': 'signal_message',
        #     'message': message
        # })
        # self.send_chat_message(content)
        print("in new message command")
        # cipher = data.get('cipher_message')
        # if cipher:
        #     print("we ot cipher", cipher)
        #     print("eb, db", self.e, self.d)
        #     array = []
        #     if (self.count == 1):
        #         for c in cipher:
        #             # print((c**self.e) % self.prime)
        #             print("c^e", c**self.e, (c**self.e) % self.prime)
        #             array.append((c**self.e) % self.prime)
        #     if (self.count == 2):
        #         for c in cipher:
        #             if c:
        #                 # print((c**self.e) % self.prime)
        #                 print(chr((c**self.d) % self.prime))
        #                 array.append(chr((c**self.d) % self.prime))
        #         print("array to send", array)
        #         values = ''.join(str(v) for v in array)
        #         dest = data.get('to')
        #         if dest:
        #             print("mes to user ", dest)
        #             room = Room.objects.filter(pk=self.room_name).first()
        #             dest_user = User.objects.filter(username=dest).first()
        #             author_user = room.user.filter(~Q(username=dest)).first()
        #             message = Message.objects.create(author=author_user,
        #                                              content=values,
        #                                              room=room)
        #             content = {
        #                 'command': 'new_message',
        #                 'message': dest_message_to_json(message)
        #             }
        #             signal_room = SignalRoom.objects.filter(
        #                 user=dest_user).first()
        #             room_group_name = 'signal_%s' % signal_room.id

        #             # notify_message = "You have a new message from " + author_user.username
        #             message = {"message": message_to_json(
        #                 message), "type": "message"}
        #             channel_layer = channels.layers.get_channel_layer()
        #             async_to_sync(channel_layer.group_send)(room_group_name, {
        #                 'type': 'signal_message',
        #                 'message': message
        #             })
        #             self.count = 1
        #             self.send_chat_message(content)
        #             print(values)
        #     # if self.count == 2:
        #     #     for a in array:
        #     #         print(chr(a))
        #     # channel_layer = channels.layers.get_channel_layer()
        #     async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
        #         'type': 'signal_message',
        #         'message': {"cipher": array}
        #     })
        #     self.count += 1

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

    def on_key_exchange(self, data):

        primebits = 9

        if self.prime == 0:
            self.count += 1
            PRIME = 263
            e, d = generate_keys(PRIME)
            while e > d:
                e, d = generate_keys(PRIME)
            self.prime = PRIME
            self.e = e
            self.d = d
            print(PRIME, e, d)
        # KEY CALCULATE

        print("room-group", self.room_group_name, "ss", self.room_name)
        notify_message = "You have a new message from " + str(self.prime)
        message = {"prime": str(self.prime), "type": "message"}
        # channel_layer = channels.layers.get_channel_layer()
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': 'signal_message',
            'message': message
        })

    def on_cipher_1(self, data):
        print("on_ci[her_1")
        token = data.get('token')
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        if user:
            cipher = data.get('cipher_message')
            if cipher:
                print("we ot cipher", cipher)
                print("eb, db", self.e, self.d)
                array = []
                for c in cipher:
                    # print((c**self.e) % self.prime)
                    # print("c^e", c**self.e, (c**self.e) % self.prime)
                    array.append((c**self.e) % self.prime)
                print("cipher1", array)
                channel_layer = channels.layers.get_channel_layer()
                async_to_sync(channel_layer.group_send)(self.room_group_name, {
                    'type': 'signal_message',
                    'message': {"cipher_1": array}
                })

    def on_cipher_2(self, data):
        print("on_ci[her_2")
        token = data.get('token')
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        if user:
            array = []
            cipher = data.get('cipher_message')
            if cipher:
                print("we ot cipher 2", cipher)
                for c in cipher:
                    if c:
                        # print((c**self.e) % self.prime)
                        print(chr((c**self.d) % self.prime))
                        array.append(chr((c**self.d) % self.prime))
                print("array to send", array)
                values = ''.join(str(v) for v in array)
                dest = data.get('to')
                print ("mes to u",dest)
                message = {"message":values}
                channel_layer = channels.layers.get_channel_layer()

                # async_to_sync(channel_layer.group_send)(self.room_group_name, {
                #     'type': 'new_message',
                #     'message': {"new_message":values,"author":user.username, "command":"new_message","content":values}
                #     # 'command':'new_message',
                # })
                if dest:
                    room = Room.objects.filter(pk=self.room_name).first()
                    dest_user = User.objects.filter(username=dest).first()
                    author_user = room.user.filter(~Q(username=dest)).first()
                    message = Message.objects.create(author=author_user,
                                                     content=values,
                                                     room=room)
                    content = {
                        'command': 'new_message',
                        'message': dest_message_to_json(message)
                    }
                    signal_room = SignalRoom.objects.filter(
                        user=dest_user).first()
                    room_group_name = 'signal_%s' % signal_room.id
                    print("delay 1")
                    # notify_message = "You have a new message from " + author_user.username
                    notify_message = {"message": message_to_json(
                        message), "type": "message"}
                    channel_layer = channels.layers.get_channel_layer()
                    async_to_sync(channel_layer.group_send)(room_group_name, {
                        'type': 'signal_message',
                        'message': notify_message
                    })
                    print("delay 2", message.created_at)
                    # self.count = 1
                    # self.send_chat_message(content)
                    # channel_layer = channels.layers.get_channel_layer()
                    # async_to_sync(self.channel_layer.group_send)(room_group_name, {
                    #     'type': 'signal_message',
                    #     'message': content
                    # })
                    async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
                    'type': 'new_message',
                    'message': {"new_message":values,"author":user.username, "command":"new_message","content":values, "created_at": str(message.created_at)}
                    })
                    print(values)
                    # await channel_layer.group_send(self.room_group_name, {
                    #     'type': 'new_message',
                    #     'message': {"new_message":values,"author":user.username, "command":"new_message","content":values, "created_at": str(message.created_at)}
                    # }

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
        'on_load_more': on_load_more,
        'on_key_exchange': on_key_exchange,
        'on_cipher_1': on_cipher_1,
        'on_cipher_2': on_cipher_2

    }

    def connect(self):
        self.prime = 0
        self.count = 0
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
        # print("mess rec")

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
        print("sending signal", message)


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


def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def generate_keys(prime):
    while True:
        e = random.randint(0, prime - 2)
        if libnum.gcd(e, prime - 1) == 1 and e > 2:
            break
    d = libnum.invmod(e, prime - 1)

    return e, d


def crypt(chunk, key, prime):
    num = 0
    for c in chunk:
        num *= 256
        num += ord(c)
    res = pow(num, key, prime)
    vect = []
    for i in range(0, len(chunk)):
        vect.append(chr(res % 256))
        res = res // 256

    return "".join(reversed(vect))

