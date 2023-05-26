from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Category, SetList, SetListSong, Song, Tag


class SetListSongInline(admin.TabularInline):
    model = SetListSong
    extra = 1
    autocomplete_fields = ['song']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'category',)
    list_filter = ('category',)
    search_fields = ('title', 'lyrics',)

@admin.register(SetList)
class SetListAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'share_link',)

    def share_link(self, obj):
        url = reverse('setlist_detail', args=[obj.pk])
        return format_html('<a href="{}">Compartir</a>', url)

    share_link.short_description = 'Compartir'

    inlines = [SetListSongInline]

@admin.register(SetListSong)
class SetListSongAdmin(admin.ModelAdmin):
    list_display = ('order', 'song', 'chord', 'setlist',)
    list_filter = ('song', 'setlist',)
    search_fields = ('song__title',)
