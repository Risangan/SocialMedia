# Generated by Django 2.1.2 on 2018-11-25 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matchingsite', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hobby',
            name='hobbyDesc',
        ),
    ]
