# Generated by Django 4.0.2 on 2022-03-11 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('website', '0005_delete_greeting'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_id', models.IntegerField()),
                ('collector_id', models.IntegerField()),
                ('response_id', models.IntegerField()),
                ('response_text', models.CharField(max_length=5000)),
                ('question_id', models.IntegerField()),
                ('row_id', models.IntegerField()),
                ('choice_id', models.IntegerField()),
                ('other_id', models.IntegerField()),
                ('choice_text', models.CharField(max_length=200)),
            ],
        ),
    ]

