from django.db import models
from django.utils.translation import gettext_lazy as _


NOTATION_CHOICES = [
    ("english", _("English (C, D, E…)")),
    ("latin", _("Latin (Do, Re, Mi…)")),
]


class Category(models.Model):
    name = models.CharField(_("name"), max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Tag(models.Model):
    name = models.CharField(_("name"), max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Song(models.Model):
    title = models.CharField(_("title"), max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name=_("category")
    )
    lyrics = models.TextField(
        _("lyrics"),
        help_text=_("Use ChordPro format: [Am]word [G]word. Chords are optional."),
    )
    original_key = models.CharField(
        _("original key"), max_length=10, blank=True, default=""
    )
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Song")
        verbose_name_plural = _("Songs")


class SetList(models.Model):
    title = models.CharField(_("title"), max_length=200)
    date = models.DateField(_("date"))
    chord_notation = models.CharField(
        _("chord notation"),
        max_length=10,
        choices=NOTATION_CHOICES,
        default="english",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Set list")
        verbose_name_plural = _("Set lists")


class SetListSong(models.Model):
    setlist = models.ForeignKey(
        SetList, related_name="songs", on_delete=models.CASCADE, verbose_name="set list"
    )
    order = models.PositiveIntegerField(_("order"))
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name=_("song"))
    chord = models.CharField(max_length=20, verbose_name=_("chord"))
    font_size = models.PositiveIntegerField(_("font size"), default=14)
    page_break_after = models.BooleanField(_("page break"), default=False)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Set list song")
        verbose_name_plural = _("Set list songs")

    def __str__(self):
        return f"{self.order} - {self.song}"
