from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Category, Organization, SetList, SetListSong, Song, Tag


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label=_("Email"))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class SongForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("Tags"),
    )

    class Meta:
        model = Song
        fields = ["title", "category", "original_key", "lyrics", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "original_key": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "C, Am, G…"}
            ),
            "lyrics": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "font-family: 'DM Mono', monospace; font-size: 0.88rem;",
                    "rows": 16,
                }
            ),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("New tag name…")}
            ),
        }


class SetListForm(forms.ModelForm):
    class Meta:
        model = SetList
        fields = ["title", "date", "chord_notation"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "chord_notation": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.date:
            self.initial["date"] = self.instance.date.strftime("%Y-%m-%d")


class SetListSongForm(forms.ModelForm):
    class Meta:
        model = SetListSong
        fields = ["song", "chord", "font_size", "page_break_after"]
        widgets = {
            "song": forms.Select(attrs={"class": "form-control"}),
            "chord": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "C, Am…"}
            ),
            "font_size": forms.NumberInput(
                attrs={"class": "form-control", "min": 8, "max": 36}
            ),
            "page_break_after": forms.CheckboxInput(),
        }


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }


class MemberAddForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label=_("Username"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Enter username…")}
        ),
    )
    role = forms.ChoiceField(
        choices=[("admin", _("Admin")), ("member", _("Member"))],
        initial="member",
        label=_("Role"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
