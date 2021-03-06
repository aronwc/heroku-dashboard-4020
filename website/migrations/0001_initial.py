# Generated by Django 4.0.4 on 2022-04-15 22:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocketCharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mag_num', models.IntegerField()),
                ('defendant', models.CharField(max_length=50)),
                ('judge', models.CharField(max_length=20)),
                ('count', models.IntegerField()),
                ('code', models.CharField(max_length=40)),
                ('charge', models.CharField(max_length=200)),
                ('bond', models.IntegerField()),
                ('date', models.DateTimeField(verbose_name='date of court session')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_id', models.BigIntegerField()),
                ('question_text', models.CharField(max_length=600)),
                ('question_type', models.CharField(max_length=30)),
                ('question_subtype', models.CharField(max_length=30)),
                ('question_clean_text', models.CharField(default='', max_length=600)),
                ('cluster_id', models.IntegerField(default=-1)),
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
        migrations.CreateModel(
            name='ResponseOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_option_id', models.CharField(max_length=40)),
                ('row_id', models.BigIntegerField()),
                ('row_text', models.CharField(max_length=300)),
                ('choice_id', models.BigIntegerField()),
                ('response_option_text', models.CharField(max_length=500)),
                ('question', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.question')),
                ('survey', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.survey')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responder_id', models.BigIntegerField()),
                ('collector_id', models.BigIntegerField()),
                ('response_text', models.CharField(max_length=5000)),
                ('row_id', models.BigIntegerField(default=0)),
                ('choice_id', models.BigIntegerField()),
                ('other_id', models.BigIntegerField()),
                ('choice_text', models.CharField(max_length=200)),
                ('choice_clean_text', models.CharField(default='', max_length=200)),
                ('question', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.question')),
                ('survey', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.survey')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='website.survey'),
        ),
        migrations.CreateModel(
            name='DocketProceeding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mag_num', models.IntegerField()),
                ('date', models.DateTimeField(verbose_name='date of court session')),
                ('judge', models.CharField(max_length=20)),
                ('text', models.CharField(max_length=5000)),
                ('bond_set_for', models.FloatField(blank=True, null=True)),
                ('mag_section', models.CharField(default='', max_length=2)),
                ('docket_charges', models.ManyToManyField(to='website.docketcharge')),
            ],
        ),
    ]
