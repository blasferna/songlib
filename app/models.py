from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


NOTATION_CHOICES = [
    ("english", _("English (C, D, E…)")),
    ("latin", _("Latin (Do, Re, Mi…)")),
]

ROLE_CHOICES = [
    ("admin", _("Admin")),
    ("member", _("Member")),
]


class Organization(models.Model):
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_organizations",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]


class Membership(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("user"),
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name=_("organization"),
    )
    role = models.CharField(
        _("role"), max_length=20, choices=ROLE_CHOICES, default="member"
    )
    created_at = models.DateTimeField(_("joined at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user} — {self.organization} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == "admin"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("user"),
    )
    active_organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("active organization"),
    )

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return f"{self.user} profile"


class Category(models.Model):
    name = models.CharField(_("name"), max_length=200)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name=_("organization")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = ("name", "organization")


class Tag(models.Model):
    name = models.CharField(_("name"), max_length=200)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name=_("organization")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        unique_together = ("name", "organization")


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
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name=_("organization")
    )

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
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name=_("organization")
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
