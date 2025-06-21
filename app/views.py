from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
import re
from .models import SetList, SetListSong
from .serializers import SetListSongSerializer
import html2text

SUPPORTED_PAGE_SIZES = ["A4", "letter", "legal"]


def html_to_plain_text(html_content):
    """
    Convierte HTML a texto plano usando la librería estándar html2text.
    Esta es la forma robusta y correcta de hacerlo.
    """
    if not html_content:
        return ""

    # 1. Crear una instancia del conversor
    h = html2text.HTML2Text()

    # 2. Configurar para que NO haga ajustes de línea automáticos.
    #    Esto es crucial para preservar las letras de las canciones tal cual.
    h.body_width = 0

    # 3. Convertir el HTML a texto
    text = h.handle(html_content)

    # 4. Limpieza final: La librería convierte <strong> en **texto**.
    #    Simplemente los eliminamos.
    text = text.replace('**', '')

    return text.strip()


def setlist_detail(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    page_size = request.GET.get("page_size", "letter")
    if page_size not in SUPPORTED_PAGE_SIZES:
        page_size = "letter"
    songs = setlist.songs.all().order_by("order")
    return render(
        request,
        "app/setlist_detail.html",
        {"setlist": setlist, "songs": songs, "page_size": page_size},
    )


def setlist_export_txt(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = setlist.songs.all().order_by("order")

    content = f"{setlist.title}\n"
    content += f"{setlist.date}\n"
    content += "=" * 50 + "\n\n"

    for song in songs:
        content += f"{song.order}. {song.song.title} - ({song.chord})\n"
        content += "-" * 30 + "\n"

        plain_lyrics = html_to_plain_text(song.song.lyrics)
        content += plain_lyrics + "\n\n"

        if song.page_break_after:
            content += "\n" + "=" * 50 + "\n\n"

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{setlist.title}.txt"'

    return response


class SetListSongViewSet(viewsets.ModelViewSet):
    queryset = SetListSong.objects.all()
    serializer_class = SetListSongSerializer
