from django.contrib import admin
from .models import Message, Room
from django_ace import AceWidget
from django import forms


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        widgets = {
            'content':
            AceWidget(mode='html',
                      theme='twilight',
                      wordwrap=True,
                      width='100%',
                      height='300px')
        }


# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'updated_at']
    raw_id_fields = ('room', )
    form = MessageForm

    class Meta:
        model = Message


class RoomAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'updated_at']

    class Meta:
        model = Room


admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin)