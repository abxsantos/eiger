# Generated by Django 4.2.3 on 2023-08-21 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='climber',
            name='trainer',
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='climbers',
                to='authentication.trainer',
            ),
        ),
    ]
