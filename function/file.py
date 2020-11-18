from django.core.files.base import ContentFile
import base64
import re


def get_image(image):
    if image:
        format, img_str = image.split(';base64,')
        ext = format.split('/')[-1]
        return ContentFile(base64.b64decode(img_str), name='temp.' + ext)


def isValidHexaCode(str):

    # Regex to check valid
    # hexadecimal color code.
    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if (str == None):
        return False

    # Return if the string
    # matched the ReGex
    if (re.search(p, str)):
        return True
    else:
        return False