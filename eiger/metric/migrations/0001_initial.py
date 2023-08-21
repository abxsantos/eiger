# Generated by Django 4.2.3 on 2023-08-21 01:29

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trainers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClimberMetric',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
                ('value', models.CharField(max_length=255)),
                (
                    'metric_type',
                    models.CharField(
                        choices=[
                            ('hangboard_max_weight', 'Hangboard Max Weight'),
                            ('hangboard_min_edge', 'Hangboard Min Edge'),
                            ('weighted_pull_ups', 'Weighted Pull-ups'),
                            (
                                'max_flash_boulder_grade',
                                'Max Flash Boulder Grade',
                            ),
                        ],
                        max_length=255,
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExerciseMetricType',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
                (
                    'metric_type',
                    models.CharField(
                        choices=[
                            ('hangboard_max_weight', 'Hangboard Max Weight'),
                            ('hangboard_min_edge', 'Hangboard Min Edge'),
                            ('weighted_pull_ups', 'Weighted Pull-ups'),
                            (
                                'max_flash_boulder_grade',
                                'Max Flash Boulder Grade',
                            ),
                        ],
                        max_length=255,
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FingerStrengthMetric',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
                (
                    'arm_protocol',
                    models.CharField(
                        choices=[
                            ('one_arm', 'One Arm'),
                            ('two_arms', 'Two Arms'),
                        ],
                        max_length=20,
                    ),
                ),
                ('weight_in_kilos', models.IntegerField(default=0)),
                (
                    'grip_type',
                    models.CharField(
                        choices=[
                            ('sloper', 'Sloper'),
                            ('pinch', 'Pinch'),
                            ('full-crimp', 'Crimp'),
                            ('open-hand', 'Open Hand'),
                            ('half-crimp', 'Half Crimp'),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    'edge_size_in_millimeters',
                    models.PositiveSmallIntegerField(default=20),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FingerStrengthMetricConfiguration',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeUnderEffortMetric',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
                ('set', models.PositiveSmallIntegerField(default=1)),
                (
                    'time_under_effort',
                    models.PositiveSmallIntegerField(default=0),
                ),
                (
                    'rest_time_in_seconds',
                    models.PositiveSmallIntegerField(default=0),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeUnderEffortMetricConfiguration',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text='The timestamp when the object was created.',
                    ),
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text=(
                            'The timestamp when the object was last updated.'
                        ),
                    ),
                ),
                (
                    'identifier',
                    models.SlugField(
                        choices=[
                            ('lactate-curve-test', 'Lactate Curve Test'),
                            ('hollow-body-hold-test', 'Hollow Body Hold Test'),
                        ]
                    ),
                ),
                (
                    'exercise',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='time_under_effort_metric_configuration',
                        to='trainers.exercise',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
