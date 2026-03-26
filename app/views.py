import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from rest_framework import viewsets

from .chords import process_chordpro, strip_chords
from .forms import (
    CategoryForm,
    RegisterForm,
    SetListForm,
    SetListSongForm,
    SongForm,
    TagForm,
)
from .models import Category, SetList, SetListSong, Song, Tag
from .serializers import SetListSongSerializer

SUPPORTED_PAGE_SIZES = ["A4", "letter", "legal"]


def _normalize_accent(text):
    """Remove diacritics for accent-insensitive search."""
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


# ─── Auth ───────────────────────────────────────────────────────────────────────


def register_view(request):
    if request.user.is_authenticated:
        return redirect("song_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Welcome! Your account has been created."))
            return redirect("song_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


# ─── Songs ──────────────────────────────────────────────────────────────────────


@login_required
def song_list(request):
    qs = Song.objects.select_related("category").prefetch_related("tags").all()
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    if q:
        q_norm = _normalize_accent(q)
        # Filter in Python for accent-insensitive search
        matching_pks = [
            s.pk
            for s in qs
            if q_norm in _normalize_accent(s.title)
            or q_norm in _normalize_accent(s.lyrics or "")
        ]
        qs = qs.filter(pk__in=matching_pks)
    if category_id:
        qs = qs.filter(category_id=category_id)
    qs = qs.order_by("title")
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.order_by("name")
    return render(
        request,
        "app/song_list.html",
        {
            "page_obj": page,
            "q": q,
            "category_id": category_id,
            "categories": categories,
            "nav_active": "songs",
        },
    )


@login_required
def song_create(request):
    if request.method == "POST":
        form = SongForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Song created."))
            return redirect("song_list")
    else:
        form = SongForm()
    selected_tags = Tag.objects.filter(pk__in=request.POST.getlist("tags")) if request.method == "POST" else Tag.objects.none()
    return render(
        request, "app/song_form.html", {"form": form, "selected_tags": selected_tags, "nav_active": "songs"}
    )


@login_required
def song_edit(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if request.method == "POST":
        form = SongForm(request.POST, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, _("Song updated."))
            return redirect("song_list")
    else:
        form = SongForm(instance=song)
    selected_tags = Tag.objects.filter(pk__in=request.POST.getlist("tags")) if request.method == "POST" else song.tags.all()
    return render(
        request,
        "app/song_form.html",
        {"form": form, "song": song, "selected_tags": selected_tags, "nav_active": "songs"},
    )


@login_required
def song_delete(request, pk):
    song = get_object_or_404(Song, pk=pk)
    if request.method == "POST":
        song.delete()
        messages.success(request, _("Song deleted."))
        return redirect("song_list")
    return render(
        request,
        "app/confirm_delete.html",
        {
            "object": song,
            "object_name": song.title,
            "cancel_url": "song_list",
            "nav_active": "songs",
        },
    )


# ─── Categories ─────────────────────────────────────────────────────────────────


@login_required
def category_list(request):
    categories = Category.objects.annotate(song_count=Count("song")).order_by("name")
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category created."))
            return redirect("category_list")
    return render(
        request,
        "app/category_list.html",
        {"categories": categories, "form": form, "nav_active": "categories"},
    )


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category updated."))
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "app/category_form.html",
        {"form": form, "category": category, "nav_active": "categories"},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    song_count = category.song_set.count()
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category deleted."))
        return redirect("category_list")
    return render(
        request,
        "app/confirm_delete.html",
        {
            "object": category,
            "object_name": category.name,
            "cancel_url": "category_list",
            "warning": (
                _("This category has %(count)d song(s) that will also be deleted.")
                % {"count": song_count}
                if song_count
                else None
            ),
            "nav_active": "categories",
        },
    )


# ─── Tags ───────────────────────────────────────────────────────────────────────


@login_required
def tag_list(request):
    tags = Tag.objects.annotate(song_count=Count("song")).order_by("name")
    form = TagForm()
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Tag created."))
            return redirect("tag_list")
    return render(
        request,
        "app/tag_list.html",
        {"tags": tags, "form": form, "nav_active": "tags"},
    )


@login_required
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, _("Tag updated."))
            return redirect("tag_list")
    else:
        form = TagForm(instance=tag)
    return render(
        request,
        "app/tag_form.html",
        {"form": form, "tag": tag, "nav_active": "tags"},
    )


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        tag.delete()
        messages.success(request, _("Tag deleted."))
        return redirect("tag_list")
    return render(
        request,
        "app/confirm_delete.html",
        {
            "object": tag,
            "object_name": tag.name,
            "cancel_url": "tag_list",
            "nav_active": "tags",
        },
    )


# ─── Set Lists ──────────────────────────────────────────────────────────────────


@login_required
def setlist_list(request):
    setlists = (
        SetList.objects.annotate(song_count=Count("songs"))
        .order_by("-date")
    )
    q = request.GET.get("q", "").strip()
    if q:
        q_norm = _normalize_accent(q)
        matching_pks = [
            sl.pk for sl in setlists if q_norm in _normalize_accent(sl.title)
        ]
        setlists = setlists.filter(pk__in=matching_pks)
    return render(
        request,
        "app/setlist_list.html",
        {"setlists": setlists, "q": q, "nav_active": "setlists"},
    )


@login_required
def setlist_create(request):
    if request.method == "POST":
        form = SetListForm(request.POST)
        if form.is_valid():
            sl = form.save()
            messages.success(request, _("Set list created."))
            return redirect("setlist_edit", pk=sl.pk)
    else:
        form = SetListForm()
    return render(
        request,
        "app/setlist_form.html",
        {"form": form, "nav_active": "setlists"},
    )


@login_required
def setlist_edit(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    if request.method == "POST":
        form = SetListForm(request.POST, instance=setlist)
        if form.is_valid():
            form.save()
            messages.success(request, _("Set list updated."))
            return redirect("setlist_edit", pk=pk)
    else:
        form = SetListForm(instance=setlist)
    setlist_songs = setlist.songs.select_related("song").order_by("order")
    all_songs = Song.objects.select_related("category").order_by("title")
    return render(
        request,
        "app/setlist_form.html",
        {
            "form": form,
            "setlist": setlist,
            "setlist_songs": setlist_songs,
            "all_songs": all_songs,
            "nav_active": "setlists",
        },
    )


@login_required
def setlist_delete(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    if request.method == "POST":
        setlist.delete()
        messages.success(request, _("Set list deleted."))
        return redirect("setlist_list")
    return render(
        request,
        "app/confirm_delete.html",
        {
            "object": setlist,
            "object_name": setlist.title,
            "cancel_url": "setlist_list",
            "nav_active": "setlists",
        },
    )


@login_required
@require_POST
def setlist_add_song(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    song_id = request.POST.get("song_id")
    chord = request.POST.get("chord", "")
    if not song_id:
        return JsonResponse({"error": "song_id required"}, status=400)
    song = get_object_or_404(Song, pk=song_id)
    max_order = setlist.songs.count()
    sls = SetListSong.objects.create(
        setlist=setlist,
        song=song,
        chord=chord or song.original_key,
        order=max_order + 1,
    )
    return JsonResponse(
        {
            "id": sls.id,
            "order": sls.order,
            "song_title": song.title,
            "chord": sls.chord,
            "font_size": sls.font_size,
            "page_break_after": sls.page_break_after,
        }
    )


@login_required
@require_POST
def setlist_remove_song(request, pk, song_pk):
    setlist = get_object_or_404(SetList, pk=pk)
    sls = get_object_or_404(SetListSong, pk=song_pk, setlist=setlist)
    sls.delete()
    # Re-order remaining
    for i, s in enumerate(setlist.songs.order_by("order"), start=1):
        if s.order != i:
            s.order = i
            s.save(update_fields=["order"])
    return JsonResponse({"ok": True})


@login_required
@require_POST
def setlist_reorder(request, pk):
    setlist = get_object_or_404(SetList, pk=pk)
    try:
        order = json.loads(request.body).get("order", [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    for i, song_id in enumerate(order, start=1):
        SetListSong.objects.filter(pk=song_id, setlist=setlist).update(order=i)
    return JsonResponse({"ok": True})


@login_required
def song_search_api(request):
    """JSON endpoint for song autocomplete."""
    q = request.GET.get("q", "").strip()
    songs = Song.objects.select_related("category").order_by("title")
    if q:
        q_norm = _normalize_accent(q)
        matching_pks = [
            s.pk for s in songs if q_norm in _normalize_accent(s.title)
        ]
        songs = songs.filter(pk__in=matching_pks)
    results = []
    for s in songs[:30]:
        results.append(
            {
                "id": s.pk,
                "title": s.title,
                "category": s.category.name if s.category else "",
                "original_key": s.original_key or "",
            }
        )
    return JsonResponse({"results": results})


@login_required
def tag_search_api(request):
    """JSON endpoint for tag autocomplete."""
    q = request.GET.get("q", "").strip()
    tags = Tag.objects.order_by("name")
    if q:
        q_norm = _normalize_accent(q)
        matching_pks = [
            t.pk for t in tags if q_norm in _normalize_accent(t.name)
        ]
        tags = tags.filter(pk__in=matching_pks)
    results = [{"id": t.pk, "name": t.name} for t in tags[:30]]
    return JsonResponse({"results": results})


# ─── Existing views ─────────────────────────────────────────────────────────────


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
