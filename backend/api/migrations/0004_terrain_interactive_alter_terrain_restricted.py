# Generated by Django 4.0 on 2022-04-12 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_run_logfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='terrain',
            name='interactive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='terrain',
            name='restricted',
            field=models.BooleanField(default=False),
        ),
    ]
