# Generated by Django 4.0.5 on 2022-10-11 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_blog_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='discount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]