# Generated by Django 3.2.9 on 2022-03-21 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20220321_0548'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocketProceeding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='date of court session')),
                ('judge', models.CharField(max_length=20)),
                ('text', models.CharField(max_length=5000)),
                ('mag_num', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.docketcharge')),
            ],
        ),
        migrations.DeleteModel(
            name='DocketProceeding_new',
        ),
    ]
