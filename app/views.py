from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from .chords import process_chordpro, strip_chords
from .models import SetList, SetListSong
from .serializers import SetListSongSerializer

SUPPORTED_PAGE_SIZES = ["A4", "letter", "legal"]


def setlist_detail(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    page_size = request.GET.get("page_size", "letter")
    if page_size not in SUPPORTED_PAGE_SIZES:
        page_size = "letter"
    songs = setlist.songs.select_related("song").order_by("order")

    songs_data = []
    for s in songs:
        songs_data.append(
            {
                "obj": s,
                "plain_lyrics": strip_chords(s.song.lyrics),
            }
        )

    return render(
        request,
        "app/setlist_detail.html",
        {
            "setlist": setlist,
            "songs": songs_data,
            "page_size": page_size,
        },
    )


def setlist_export_txt(request, setlist_id):
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = setlist.songs.select_related("song").order_by("order")
    include_chords = request.GET.get("chords") == "1"

    content = f"{setlist.title}\n"
    content += f"{setlist.date}\n"
    content += "=" * 50 + "\n\n"

    for song in songs:
        content += f"{song.order}. {song.song.title} - ({song.chord})\n"
        content += "-" * 30 + "\n"

        if include_chords:
            lines = process_chordpro(
                song.song.lyrics,
                original_key=song.song.original_key,
                target_key=song.chord,
                notation=setlist.chord_notation,
            )
            for line in lines:
                chord_row = ""
                text_row = ""
                for seg in line:
                    chord_str = seg["chord"] or ""
                    text_str = seg["text"]
                    width = max(len(chord_str), len(text_str)) + 1
                    chord_row += chord_str.ljust(width)
                    text_row += text_str.ljust(width)
                chord_row = chord_row.rstrip()
                if chord_row:
                    content += chord_row + "\n"
                content += text_row.rstrip() + "\n"
        else:
            content += strip_chords(song.song.lyrics) + "\n\n"

        if song.page_break_after:
            content += "\n" + "=" * 50 + "\n\n"

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{setlist.title}.txt"'

    return response


def setlist_reader(request, setlist_id):
    """Public reader page — one song at a time, with optional chord toggle."""
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = list(setlist.songs.select_related("song").order_by("order"))
    total = len(songs)

    # Build song list for navigation (always needed)
    song_list = [
        {"index": i, "title": s.song.title, "chord": s.chord}
        for i, s in enumerate(songs)
    ]

    base_ctx = {
        "setlist": setlist,
        "total": total,
        "song_list": song_list,
    }

    if total == 0:
        return render(
            request,
            "app/setlist_reader.html",
            {**base_ctx, "current_song": None, "is_cover": True},
        )

    # Cover page when no ?song param or ?song=cover
    song_param = request.GET.get("song", "cover")
    if song_param == "cover":
        return render(
            request,
            "app/setlist_reader.html",
            {**base_ctx, "current_song": None, "is_cover": True},
        )

    # Song page
    try:
        song_index = int(song_param)
    except (ValueError, TypeError):
        song_index = 0
    song_index = max(0, min(song_index, total - 1))

    current = songs[song_index]

    # Process chords: transpose from original_key → setlist entry chord, in setlist notation
    processed_lines = process_chordpro(
        current.song.lyrics,
        original_key=current.song.original_key,
        target_key=current.chord,
        notation=setlist.chord_notation,
    )

    plain_lyrics = strip_chords(current.song.lyrics)

    return render(
        request,
        "app/setlist_reader.html",
        {
            **base_ctx,
            "is_cover": False,
            "current_song": current,
            "processed_lines": processed_lines,
            "plain_lyrics": plain_lyrics,
            "song_index": song_index,
            "has_prev": song_index > 0,
            "has_next": song_index < total - 1,
            "prev_index": song_index - 1,
            "next_index": song_index + 1,
        },
    )


class SetListSongViewSet(viewsets.ModelViewSet):
    queryset = SetListSong.objects.all()
    serializer_class = SetListSongSerializer
