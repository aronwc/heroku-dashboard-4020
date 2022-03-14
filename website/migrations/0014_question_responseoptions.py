# Generated by Django 3.2.9 on 2022-03-13 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_auto_20220313_0210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_id', models.BigIntegerField()),
                ('question_text', models.CharField(max_length=600)),
                ('question_type', models.CharField(max_length=30)),
                ('question_subtype', models.CharField(max_length=30)),
                ('survey_id', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ResponseOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_option_id', models.CharField(max_length=40)),
                ('survey_id', models.BigIntegerField()),
                ('question_id', models.BigIntegerField()),
                ('row_id', models.BigIntegerField()),
                ('row_text', models.CharField(max_length=300)),
                ('choice_id', models.BigIntegerField()),
                ('response_option_text', models.CharField(max_length=500)),
            ],
        ),
    ]