# Generated by Django 3.2.9 on 2022-03-09 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_delete_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='responses',
            name='year',
            field=models.IntegerField(choices=[('2018', '2018'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021')], default='2021', max_length=4),
        ),
        migrations.AlterField(
            model_name='responses',
            name='judge',
            field=models.CharField(choices=[('Municipal', (('Sens', 'Sens'), ('Jones', 'Jones'), ('Larche-Mason', 'Larche-Mason'), ('Shea', 'Shea'), ('Early', 'Early'), ('Landry', 'Landry'), ('Jupiter', 'Jupiter'))), ('Magistrate', (('Lombard', 'Lombard'), ('Collins', 'Collins'), ('Thibodeaux', 'Thibodeaux'), ('Blackburn', 'Blackburn'), ('Friedman', 'Friedman'))), ('Criminal', (('White', 'White'), ('Davillier', 'Davillier'), ('Willard', 'Willard'), ('Holmes', 'Holmes'), ('Goode-Douglas', 'Goode-Douglas'), ('Pittman', 'Pittman'), ('Campbell', 'Campbell'), ('Buras', 'Buras'), ('Herman', 'Herman'), ('Derbigny', 'Derbigny'), ('DeLarge', 'DeLarge'), ('Harris', 'Harris'))), ("Don't know", "Don't know")], default='Sens', max_length=80),
        ),
    ]
