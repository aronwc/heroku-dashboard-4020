# Generated by Django 4.0.2 on 2022-03-13 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='choice_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='response',
            name='collector_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='response',
            name='other_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='response',
            name='question_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='response',
            name='response_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='response',
            name='row_id',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='response',
            name='survey_id',
            field=models.BigIntegerField(),
        ),
    ]
