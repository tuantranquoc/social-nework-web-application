from django.contrib import admin

# Register your models here.
from .models import Profile
from post.models import PositivePoint


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__', '__time__','__point__']

    class Meta:
        model = Profile


class PointAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__', '__point__']

    class Meta:
        model = PositivePoint


admin.site.register(Profile, ProfileAdmin)
admin.site.register(PositivePoint, PointAdmin)
