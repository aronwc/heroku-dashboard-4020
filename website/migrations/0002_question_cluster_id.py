# Generated by Django 4.0.2 on 2022-03-22 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='cluster_id',
            field=models.IntegerField(default=-1),
        ),
    ]
