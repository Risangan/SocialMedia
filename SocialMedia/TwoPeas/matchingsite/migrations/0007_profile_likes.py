# Generated by Django 2.1.2 on 2018-12-10 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingsite', '0006_auto_20181207_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='_profile_likes_+', to='matchingsite.Profile'),
        ),
    ]
