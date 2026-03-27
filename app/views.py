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
    MemberAddForm,
    OrganizationForm,
    RegisterForm,
    SetListForm,
    SetListSongForm,
    SongForm,
    TagForm,
)
from .models import Category, Membership, Organization, SetList, SetListSong, Song, Tag, UserProfile
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
            # Create a default personal organization
            org = Organization.objects.create(
                name=_("%(username)s's Organization") % {"username": user.username},
                created_by=user,
            )
            Membership.objects.create(user=user, organization=org, role="admin")
            profile, _created = UserProfile.objects.get_or_create(user=user)
            profile.active_organization = org
            profile.save()
            login(request, user)
            messages.success(request, _("Welcome! Your account has been created."))
            return redirect("song_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


# ─── Songs ──────────────────────────────────────────────────────────────────────


@login_required
def song_list(request):
    org = request.active_organization
    qs = Song.objects.filter(organization=org).select_related("category").prefetch_related("tags")
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
    categories = Category.objects.filter(organization=org).order_by("name")
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
    org = request.active_organization
    if request.method == "POST":
        form = SongForm(request.POST)
        form.instance.organization = org
        if form.is_valid():
            song = form.save(commit=False)
            song.organization = org
            song.save()
            form.save_m2m()
            messages.success(request, _("Song created."))
            return redirect("song_list")
    else:
        form = SongForm()
    form.fields["category"].queryset = Category.objects.filter(organization=org)
    form.fields["tags"].queryset = Tag.objects.filter(organization=org)
    selected_tags = Tag.objects.filter(pk__in=request.POST.getlist("tags")) if request.method == "POST" else Tag.objects.none()
    return render(
        request, "app/song_form.html", {"form": form, "selected_tags": selected_tags, "nav_active": "songs"}
    )


@login_required
def song_edit(request, pk):
    org = request.active_organization
    song = get_object_or_404(Song, pk=pk, organization=org)
    if request.method == "POST":
        form = SongForm(request.POST, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, _("Song updated."))
            return redirect("song_list")
    else:
        form = SongForm(instance=song)
    form.fields["category"].queryset = Category.objects.filter(organization=org)
    form.fields["tags"].queryset = Tag.objects.filter(organization=org)
    selected_tags = Tag.objects.filter(pk__in=request.POST.getlist("tags")) if request.method == "POST" else song.tags.all()
    return render(
        request,
        "app/song_form.html",
        {"form": form, "song": song, "selected_tags": selected_tags, "nav_active": "songs"},
    )


@login_required
def song_delete(request, pk):
    song = get_object_or_404(Song, pk=pk, organization=request.active_organization)
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
    org = request.active_organization
    categories = Category.objects.filter(organization=org).annotate(song_count=Count("song")).order_by("name")
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.organization = org
            cat.save()
            messages.success(request, _("Category created."))
            return redirect("category_list")
    return render(
        request,
        "app/category_list.html",
        {"categories": categories, "form": form, "nav_active": "categories"},
    )


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, organization=request.active_organization)
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
    category = get_object_or_404(Category, pk=pk, organization=request.active_organization)
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
    org = request.active_organization
    tags = Tag.objects.filter(organization=org).annotate(song_count=Count("song")).order_by("name")
    form = TagForm()
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.organization = org
            tag.save()
            messages.success(request, _("Tag created."))
            return redirect("tag_list")
    return render(
        request,
        "app/tag_list.html",
        {"tags": tags, "form": form, "nav_active": "tags"},
    )


@login_required
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk, organization=request.active_organization)
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
    tag = get_object_or_404(Tag, pk=pk, organization=request.active_organization)
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
    org = request.active_organization
    setlists = (
        SetList.objects.filter(organization=org).annotate(song_count=Count("songs"))
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
    org = request.active_organization
    if request.method == "POST":
        form = SetListForm(request.POST)
        if form.is_valid():
            sl = form.save(commit=False)
            sl.organization = org
            sl.save()
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
    org = request.active_organization
    setlist = get_object_or_404(SetList, pk=pk, organization=org)
    if request.method == "POST":
        form = SetListForm(request.POST, instance=setlist)
        if form.is_valid():
            form.save()
            messages.success(request, _("Set list updated."))
            return redirect("setlist_edit", pk=pk)
    else:
        form = SetListForm(instance=setlist)
    setlist_songs = setlist.songs.select_related("song").order_by("order")
    all_songs = Song.objects.filter(organization=org).select_related("category").order_by("title")
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
    setlist = get_object_or_404(SetList, pk=pk, organization=request.active_organization)
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
    setlist = get_object_or_404(SetList, pk=pk, organization=request.active_organization)
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
    setlist = get_object_or_404(SetList, pk=pk, organization=request.active_organization)
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
    setlist = get_object_or_404(SetList, pk=pk, organization=request.active_organization)
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
    org = request.active_organization
    q = request.GET.get("q", "").strip()
    songs = Song.objects.filter(organization=org).select_related("category").order_by("title")
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
    org = request.active_organization
    q = request.GET.get("q", "").strip()
    tags = Tag.objects.filter(organization=org).order_by("name")
    if q:
        q_norm = _normalize_accent(q)
        matching_pks = [
            t.pk for t in tags if q_norm in _normalize_accent(t.name)
        ]
        tags = tags.filter(pk__in=matching_pks)
    results = [{"id": t.pk, "name": t.name} for t in tags[:30]]
    return JsonResponse({"results": results})


@login_required
def user_search_api(request):
    """JSON endpoint for user autocomplete (member add)."""
    from django.contrib.auth.models import User

    q = request.GET.get("q", "").strip()
    org_pk = request.GET.get("org")
    users = User.objects.filter(is_active=True).order_by("username")
    if q:
        q_norm = _normalize_accent(q)
        matching_pks = [
            u.pk for u in users if q_norm in _normalize_accent(u.username) or (u.email and q_norm in _normalize_accent(u.email))
        ]
        users = users.filter(pk__in=matching_pks)
    # Exclude users already in this organization
    if org_pk:
        existing = Membership.objects.filter(organization_id=org_pk).values_list("user_id", flat=True)
        users = users.exclude(pk__in=existing)
    results = [
        {"id": u.pk, "username": u.username, "email": u.email or ""}
        for u in users[:30]
    ]
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
    """Public reader page — single-page with all songs for offline sharing."""
    setlist = get_object_or_404(SetList, id=setlist_id)
    songs = list(setlist.songs.select_related("song").order_by("order"))
    total = len(songs)

    # Build full song data for every song (all rendered at once for offline use)
    all_songs = []
    for i, s in enumerate(songs):
        processed_lines = process_chordpro(
            s.song.lyrics,
            original_key=s.song.original_key,
            target_key=s.chord,
            notation=setlist.chord_notation,
        )
        plain_lyrics = strip_chords(s.song.lyrics)
        all_songs.append({
            "index": i,
            "title": s.song.title,
            "chord": s.chord,
            "processed_lines": processed_lines,
            "plain_lyrics": plain_lyrics,
        })

    return render(
        request,
        "app/setlist_reader.html",
        {
            "setlist": setlist,
            "total": total,
            "all_songs": all_songs,
        },
    )


class SetListSongViewSet(viewsets.ModelViewSet):
    queryset = SetListSong.objects.all()
    serializer_class = SetListSongSerializer


# ─── Organizations ──────────────────────────────────────────────────────────────


@login_required
def organization_list(request):
    memberships = Membership.objects.filter(user=request.user).select_related(
        "organization"
    )
    return render(
        request,
        "app/organization_list.html",
        {"memberships": memberships, "nav_active": "organizations"},
    )


@login_required
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = form.save(commit=False)
            org.created_by = request.user
            org.save()
            Membership.objects.create(
                user=request.user, organization=org, role="admin"
            )
            # Set as active organization
            profile, _created = UserProfile.objects.get_or_create(user=request.user)
            profile.active_organization = org
            profile.save()
            messages.success(request, _("Organization created."))
            return redirect("song_list")
    else:
        form = OrganizationForm()
    return render(
        request,
        "app/organization_form.html",
        {"form": form, "nav_active": "organizations"},
    )


@login_required
def organization_edit(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    membership = get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            messages.success(request, _("Organization updated."))
            return redirect("organization_list")
    else:
        form = OrganizationForm(instance=org)
    return render(
        request,
        "app/organization_form.html",
        {"form": form, "organization": org, "nav_active": "organizations"},
    )


@login_required
def organization_delete(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    membership = get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    song_count = Song.objects.filter(organization=org).count()
    setlist_count = SetList.objects.filter(organization=org).count()
    if request.method == "POST":
        # If this was the active org, clear it
        profile = request.user.profile
        if profile.active_organization == org:
            # Switch to another org if available
            other = (
                Membership.objects.filter(user=request.user)
                .exclude(organization=org)
                .select_related("organization")
                .first()
            )
            profile.active_organization = other.organization if other else None
            profile.save()
        org.delete()
        messages.success(request, _("Organization deleted."))
        return redirect("organization_list")
    return render(
        request,
        "app/confirm_delete.html",
        {
            "object": org,
            "object_name": org.name,
            "cancel_url": "organization_list",
            "warning": _("This will delete %(songs)d song(s) and %(setlists)d set list(s).")
            % {"songs": song_count, "setlists": setlist_count}
            if song_count or setlist_count
            else None,
            "nav_active": "organizations",
        },
    )


@login_required
def organization_switch(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    get_object_or_404(Membership, user=request.user, organization=org)
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    profile.active_organization = org
    profile.save()
    messages.success(
        request, _("Switched to %(org)s.") % {"org": org.name}
    )
    return redirect("song_list")


@login_required
def organization_members(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    user_membership = get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    memberships = Membership.objects.filter(organization=org).select_related("user")
    form = MemberAddForm()
    return render(
        request,
        "app/organization_members.html",
        {
            "organization": org,
            "memberships": memberships,
            "form": form,
            "nav_active": "organizations",
        },
    )


@login_required
@require_POST
def organization_add_member(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    form = MemberAddForm(request.POST)
    if form.is_valid():
        from django.contrib.auth.models import User

        username = form.cleaned_data["username"]
        role = form.cleaned_data["role"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, _("User '%(username)s' not found.") % {"username": username})
            return redirect("organization_members", pk=pk)
        membership, created = Membership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={"role": role},
        )
        if created:
            messages.success(
                request,
                _("%(username)s added to the organization.") % {"username": username},
            )
        else:
            messages.warning(
                request,
                _("%(username)s is already a member.") % {"username": username},
            )
    return redirect("organization_members", pk=pk)


@login_required
@require_POST
def organization_remove_member(request, pk, user_id):
    org = get_object_or_404(Organization, pk=pk)
    get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    membership = get_object_or_404(Membership, organization=org, user_id=user_id)
    if membership.user == request.user:
        # Cannot remove yourself if you're the only admin
        admin_count = Membership.objects.filter(
            organization=org, role="admin"
        ).count()
        if admin_count <= 1:
            messages.error(request, _("Cannot remove the only admin."))
            return redirect("organization_members", pk=pk)
    membership.delete()
    messages.success(request, _("Member removed."))
    return redirect("organization_members", pk=pk)


@login_required
@require_POST
def organization_change_role(request, pk, user_id):
    org = get_object_or_404(Organization, pk=pk)
    get_object_or_404(
        Membership, user=request.user, organization=org, role="admin"
    )
    membership = get_object_or_404(Membership, organization=org, user_id=user_id)
    if membership.role == "admin":
        # Prevent removing last admin
        admin_count = Membership.objects.filter(
            organization=org, role="admin"
        ).count()
        if admin_count <= 1:
            messages.error(request, _("Cannot demote the only admin."))
            return redirect("organization_members", pk=pk)
        membership.role = "member"
    else:
        membership.role = "admin"
    membership.save()
    messages.success(
        request,
        _("%(username)s is now %(role)s.")
        % {"username": membership.user.username, "role": membership.get_role_display()},
    )
    return redirect("organization_members", pk=pk)
