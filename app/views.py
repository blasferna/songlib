from django.shortcuts import get_object_or_404, render

from .models import SetList


def setlist_detail(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = setlist.songs.all().order_by('order')
    return render(request, 'app/setlist_detail.html', {'setlist': setlist, 'songs': songs})
