# Generated by Django 3.2.16 on 2024-07-27 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_code',
            field=models.CharField(blank=True, max_length=3, null=True, unique=True),
        ),
        migrations.DeleteModel(
            name='RecipeShortLink',
        ),
    ]
