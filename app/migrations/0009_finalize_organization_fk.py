# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_populate_default_organization'),
    ]

    operations = [
        # Make organization non-nullable on Category
        migrations.AlterField(
            model_name='category',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='app.organization',
                verbose_name='organization',
            ),
        ),
        # Make organization non-nullable on Tag
        migrations.AlterField(
            model_name='tag',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='app.organization',
                verbose_name='organization',
            ),
        ),
        # Make organization non-nullable on Song
        migrations.AlterField(
            model_name='song',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='app.organization',
                verbose_name='organization',
            ),
        ),
        # Make organization non-nullable on SetList
        migrations.AlterField(
            model_name='setlist',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='app.organization',
                verbose_name='organization',
            ),
        ),
        # Add unique_together constraints
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('name', 'organization')},
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('name', 'organization')},
        ),
    ]
