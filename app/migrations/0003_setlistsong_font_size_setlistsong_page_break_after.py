# Generated by Django 4.2.1 on 2023-05-26 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_category_options_alter_setlist_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='setlistsong',
            name='font_size',
            field=models.PositiveIntegerField(default=14, verbose_name='font size'),
        ),
        migrations.AddField(
            model_name='setlistsong',
            name='page_break_after',
            field=models.BooleanField(default=False, verbose_name='page break'),
        ),
    ]
