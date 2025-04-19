import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
import imghdr


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = imghdr.what(None, h=base64.b64decode(imgstr))
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)
