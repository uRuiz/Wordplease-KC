# -*- coding: utf-8 -*-
from django.conf import settings

DOWNLOAD_IMAGES = getattr(settings, 'DOWNLOAD_IMAGES', True)
THUMBNAIL_SIZE = getattr(settings, 'THUMBNAIL_SIZE', (800, 600))
