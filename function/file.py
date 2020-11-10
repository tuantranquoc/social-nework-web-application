from django.core.files.base import ContentFile
import base64


def get_image(image):
    if image:
        format, img_str = image.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(img_str), name='temp.' + ext)