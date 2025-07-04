from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, SetList, SetListSong, Song, Tag


class SetListSongInline(SortableTabularInline):
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
class SetListAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('title', 'date', 'print_lint', 'export_as_txt',)

    def print_lint(self, obj):
        url = reverse('setlist_detail', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, _("Print"))

    print_lint.short_description = _('Print')
    
    def export_as_txt(self, obj):
        url = reverse('setlist_export_txt', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, _("Export as TXT"))
    export_as_txt.short_description = _('Export as TXT')

    inlines = [SetListSongInline]

@admin.register(SetListSong)
class SetListSongAdmin(admin.ModelAdmin):
    list_display = ('order', 'song', 'chord', 'setlist',)
    list_filter = ('song', 'setlist',)
    search_fields = ('song__title',)
