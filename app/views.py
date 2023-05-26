from django.shortcuts import get_object_or_404, render

from .models import SetList

from rest_framework import viewsets
from .models import SetListSong
from .serializers import SetListSongSerializer


def setlist_detail(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = setlist.songs.all().order_by("order")
    return render(
        request, "app/setlist_detail.html", {"setlist": setlist, "songs": songs}
    )


class SetListSongViewSet(viewsets.ModelViewSet):
    queryset = SetListSong.objects.all()
    serializer_class = SetListSongSerializer
