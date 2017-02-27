# -*- coding: utf-8 -*-
from blogs.settings import THUMBNAIL_SIZE
from celery import shared_task
import os
import requests
from django.conf import settings
from PIL import Image


@shared_task  # makes this function a celery task
def download_resize_update_photo_image(post):
    image_url = post.image_url
    extension = image_url.split('/')[-1].split('.')[-1]
    file_basename = '{0}.{1}'.format(post.pk, extension)
    filename = os.path.join(settings.MEDIA_ROOT, file_basename)

    r = requests.get(image_url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    post.image_url = settings.BASE_URL + settings.MEDIA_URL + file_basename
    post.save()

    thumb_basename = '{0}-thumbnail.{1}'.format(post.pk, extension)
    thumb_path = os.path.join(settings.MEDIA_ROOT, thumb_basename)

    img = Image.open(filename)
    img.thumbnail(THUMBNAIL_SIZE)
    img.save(thumb_path, img.format)

    post.image_url = settings.BASE_URL + settings.MEDIA_URL + thumb_basename
    post.save()

