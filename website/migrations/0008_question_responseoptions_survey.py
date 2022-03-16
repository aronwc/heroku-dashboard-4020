# Generated by Django 4.0.2 on 2022-03-13 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_alter_response_choice_id_alter_response_collector_id_and_more'),
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
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_id', models.BigIntegerField()),
                ('survey_year', models.IntegerField()),
                ('survey_name', models.CharField(max_length=100)),
                ('survey_use_start_date', models.IntegerField()),
                ('survey_use_end_date', models.IntegerField()),
                ('survey_phase_id', models.IntegerField()),
                ('survey_phase_venue_type', models.CharField(max_length=15)),
                ('survey_part_id', models.CharField(max_length=10)),
                ('survey_observation_level', models.CharField(max_length=15)),
                ('observer_type', models.CharField(max_length=40)),
                ('court_id', models.CharField(max_length=20)),
                ('survey_notes', models.CharField(max_length=40)),
            ],
        ),
    ]
