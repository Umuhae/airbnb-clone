# Generated by Django 2.2.5 on 2020-12-15 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_remove_photo_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='beths',
            new_name='baths',
        ),
    ]