from rest_framework import serializers
from .models import SetListSong


class SetListSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetListSong
        fields = ["font_size", "page_break_after"]
