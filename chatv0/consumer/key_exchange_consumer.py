from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.number import getPrime
from Cryptodome.Cipher import AES
import hexdump
import sys
import random
import libnum
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
        self.send_chat_message(content)
        cipher = data.get('cipher_message')
        if cipher:
            print("we ot cipher", cipher)
            print("eb, db", self.e, self.d)
            array = []
            if (self.count == 1):
                for c in cipher:
                    # print((c**self.e) % self.prime)
                    print("c^e", c**self.e, (c**self.e) % self.prime)
                    array.append((c**self.e) % self.prime)
            if (self.count == 2):
                for c in cipher:
                    # print((c**self.e) % self.prime)
                    print(chr((c**self.d) % self.prime))
                    array.append(chr((c**self.d) % self.prime))
            print("array to send", array)
            values = ','.join(str(v) for v in array)

            print(values)
            # if self.count == 2:
            #     for a in array:
            #         print(chr(a))
            # channel_layer = channels.layers.get_channel_layer()
            async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
                'type': 'signal_message',
                'message': {"cipher": array}
            })
            self.count += 1

    def on_connect(self, data):
        print("token-on-connect-key-exchange", data['token'])
        token = data['token']
        cipher = data.get('cipher_message')
        access_token = AccessToken(str(token))
        user = User.objects.filter(pk=access_token['user_id']).first()
        print("got user", user)
        if cipher:
            print("we ot cipher", cipher)
            print("eb, db", self.e, self.d)
            array = []
            if (self.count == 1):
                for c in cipher:
                    # print((c**self.e) % self.prime)
                    print("c^e", c**self.e, (c**self.e) % self.prime)
                    array.append((c**self.e) % self.prime)
            if (self.count == 2):
                for c in cipher:
                    # print((c**self.e) % self.prime)
                    print(chr((c**self.d) % self.prime))
                    array.append(chr((c**self.d) % self.prime))
            print("array to send", array)
            values = ','.join(str(v) for v in array)

            print(values)
            # if self.count == 2:
            #     for a in array:
            #         print(chr(a))
            # channel_layer = channels.layers.get_channel_layer()
            async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
                'type': 'signal_message',
                'message': {"cipher": array}
            })
            self.count += 1

        # if user:
        #     room = Room.objects.filter(pk=self.room_name, user=user).first()
        #     messages = Message.objects.filter(room=room)
        #     if room:
        #         content = {
        #             'signal': "connected to open socket",
        #             'user': user.username
        #         }
        #         self.send_chat_message(content)
        # room_group_name = 'signal_%s' % self.room_group_name
        primebits = 9
        # if (len(sys.argv) > 1):
        #     primebits = int(sys.argv[1])
        if self.prime == 0:
            self.count += 1
            PRIME = 263
            # while PRIME < 256:
            #     PRIME = getPrime(primebits, randfunc=get_random_bytes)
            #     print(PRIME)
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
        message = {"message": str(self.prime), "type": "message"}
        # channel_layer = channels.layers.get_channel_layer()
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': 'signal_message',
            'message': message
        })

    def on_key_exchange(self, data):
        # if user:
        #     room = Room.objects.filter(pk=self.room_name, user=user).first()
        #     messages = Message.objects.filter(room=room)
        #     if room:
        #         content = {
        #             'signal': "connected to open socket",
        #             'user': user.username
        #         }
        #         self.send_chat_message(content)
        # room_group_name = 'signal_%s' % self.room_group_name
        primebits = 9
        # if (len(sys.argv) > 1):
        #     primebits = int(sys.argv[1])
        if self.prime == 0:
            self.count += 1
            PRIME = 263
            # while PRIME < 256:
            #     PRIME = getPrime(primebits, randfunc=get_random_bytes)
            #     print(PRIME)
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
        message = {"message": str(self.prime), "type": "message"}
        # channel_layer = channels.layers.get_channel_layer()
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': 'signal_message',
            'message': message
        })

    def on_signal(self, data):
        print('hello world aaa')

    command = {
        'fetch_message': fetch_message,
        'new_message': new_message,
        'on_connect': on_connect,
        'on_signal': on_signal,
        'on_key_exchange': on_key_exchange
        # 'cipher_exchange': cipher_exchange
    }

    def connect(self):
        self.prime = 0
        self.count = 0
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
        # self.send_chat_message(message)

    def cipher_message(self, event):
        message = event['cipher_message']
        print('rec-mess', message)
        # self.send_chat_message(message)


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
