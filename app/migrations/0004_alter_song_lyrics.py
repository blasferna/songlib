# Generated by Django 4.2.1 on 2023-05-26 18:16

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_setlistsong_font_size_setlistsong_page_break_after'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='lyrics',
            field=ckeditor.fields.RichTextField(verbose_name='lyrics'),
        ),
    ]