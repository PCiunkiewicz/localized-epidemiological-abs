# Generated by Django 5.1.5 on 2025-05-14 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_agentconfig_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='run',
            name='parallel',
        ),
    ]
