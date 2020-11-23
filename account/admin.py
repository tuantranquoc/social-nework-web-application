from django.contrib import admin

# Register your models here.
from .models import Profile, CustomColor
from post.models import PositivePoint


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__', '__time__', '__point__', '__follower__']

    class Meta:
        model = Profile


class PointAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__', '__point__']

    class Meta:
        model = PositivePoint
        
class CustomColorAdmin(admin.ModelAdmin):
    list_display = ['__str__']

    class Meta:
        model = CustomColor


admin.site.register(Profile, ProfileAdmin)
admin.site.register(PositivePoint, PointAdmin)
admin.site.register(CustomColor, CustomColorAdmin)
