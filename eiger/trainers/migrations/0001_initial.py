# Generated by Django 4.2.2 on 2023-06-27 00:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
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
                    'name',
                    models.CharField(
                        help_text='The name of the category.',
                        max_length=30,
                        unique=True,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ExerciseType',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
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
                    'name',
                    models.CharField(
                        help_text='The name of the exercise type.',
                        max_length=30,
                        unique=True,
                    ),
                ),
                (
                    'category',
                    models.ForeignKey(
                        help_text=(
                            'The category to which this exercise type belongs.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        to='trainers.category',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Exercise Type',
                'verbose_name_plural': 'Exercise Types',
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
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
                    'name',
                    models.CharField(
                        db_index=True,
                        help_text='The name of the exercise.',
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    'description',
                    models.TextField(
                        blank=True, help_text='A description of the exercise.'
                    ),
                ),
                (
                    'reviewed',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Indicates whether the exercise has been reviewed.'
                        ),
                    ),
                ),
                (
                    'should_add_weight',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Indicates whether weight should be added to this'
                            ' exercise.'
                        ),
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        help_text='The user who created the exercise.',
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'exercise_type',
                    models.ForeignKey(
                        help_text='The type of exercise.',
                        on_delete=django.db.models.deletion.CASCADE,
                        to='trainers.exercisetype',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Exercise',
                'verbose_name_plural': 'Exercises',
            },
        ),
        migrations.CreateModel(
            name='ExerciseVariation',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
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
                    'sets',
                    models.PositiveSmallIntegerField(
                        help_text='The number of sets in this variation.',
                        null=True,
                    ),
                ),
                (
                    'repetitions',
                    models.PositiveSmallIntegerField(
                        help_text=(
                            'The number of repetitions per set in this'
                            ' variation.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'seconds_per_repetition',
                    models.PositiveSmallIntegerField(
                        help_text=(
                            'The duration of each repetition in seconds.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'rest_per_set_in_seconds',
                    models.PositiveSmallIntegerField(
                        help_text=(
                            'The duration of rest between sets in seconds.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'rest_per_repetition_in_seconds',
                    models.PositiveSmallIntegerField(
                        help_text=(
                            'The duration of rest between repetitions in'
                            ' seconds.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'weight_in_kilos',
                    models.PositiveSmallIntegerField(
                        help_text=(
                            'The weight used in this variation in kilograms.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'reviewed',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'Indicates whether the exercise variation has been'
                            ' reviewed.'
                        ),
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        help_text=(
                            'The user who created the exercise variation.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'exercise',
                    models.ForeignKey(
                        help_text=(
                            'The exercise for which this variation is defined.'
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        to='trainers.exercise',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Exercise Variation',
                'verbose_name_plural': 'Exercise Variations',
            },
        ),
        migrations.AddConstraint(
            model_name='exercisevariation',
            constraint=models.UniqueConstraint(
                fields=(
                    'exercise',
                    'sets',
                    'repetitions',
                    'seconds_per_repetition',
                    'rest_per_set_in_seconds',
                    'rest_per_repetition_in_seconds',
                    'weight_in_kilos',
                ),
                name='unique_exercise_variation',
            ),
        ),
        migrations.AddConstraint(
            model_name='exercisetype',
            constraint=models.UniqueConstraint(
                fields=('category', 'name'), name='unique_exercise_type'
            ),
        ),
    ]
