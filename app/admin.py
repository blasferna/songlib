from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Membership, Organization, SetList, SetListSong, Song, Tag, UserProfile


class SetListSongInline(SortableTabularInline):
    model = SetListSong
    extra = 1
    autocomplete_fields = ['song']


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 1


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_by', 'created_at')
    search_fields = ('name',)
    inlines = [MembershipInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'created_at')
    list_filter = ('role', 'organization')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'active_organization')
    list_filter = ('active_organization',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')
    list_filter = ('organization',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')
    list_filter = ('organization',)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'original_key', 'organization')
    list_filter = ('category', 'organization')
    search_fields = ('title', 'lyrics',)

@admin.register(SetList)
class SetListAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ('title', 'date', 'chord_notation', 'organization', 'print_lint', 'export_as_txt', 'reader_link',)

    def print_lint(self, obj):
        url = reverse('setlist_detail', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, _("Print"))

    print_lint.short_description = _('Print')
    
    def export_as_txt(self, obj):
        url = reverse('setlist_export_txt', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, _("Export as TXT"))
    export_as_txt.short_description = _('Export as TXT')

    def reader_link(self, obj):
        url = reverse('setlist_reader', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', url, _("Reader"))
    reader_link.short_description = _('Reader')

    inlines = [SetListSongInline]

@admin.register(SetListSong)
class SetListSongAdmin(admin.ModelAdmin):
    list_display = ('order', 'song', 'chord', 'setlist',)
    list_filter = ('song', 'setlist',)
    search_fields = ('song__title',)
