# Generated by Django 3.2.9 on 2022-04-16 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20220415_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docketproceeding',
            name='mag_section',
            field=models.CharField(default='', max_length=3),
        ),
    ]
