# -*- coding: utf-8 -*-
from files.models import File
from rest_framework import serializers


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        read_only_fields = ('owner',)
