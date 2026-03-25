"""
Data migration: convert existing HTML lyrics to plain text.

Uses html2text to strip HTML tags from Song.lyrics so the field
can store ChordPro plain-text format going forward.
"""

from django.db import migrations

import html2text


def convert_html_to_plain(apps, schema_editor):
    Song = apps.get_model("app", "Song")
    h = html2text.HTML2Text()
    h.body_width = 0

    for song in Song.objects.all():
        if song.lyrics and ("<" in song.lyrics):
            text = h.handle(song.lyrics)
            text = text.replace("**", "")
            song.lyrics = text.strip()
            song.save(update_fields=["lyrics"])


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_song_plain_text_lyrics_original_key_setlist_notation"),
    ]

    operations = [
        migrations.RunPython(
            convert_html_to_plain,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
