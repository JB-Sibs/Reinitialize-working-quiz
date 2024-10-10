# Generated by Django 5.0.7 on 2024-10-09 09:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_app', '0007_remove_grade_course_id_remove_grade_assignment_id_and_more'),
        ('quizzes', '0006_alter_quiz_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='quizzes.quiz'),
        ),
        migrations.CreateModel(
            name='ExamResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_name', models.CharField(max_length=255)),
                ('score', models.FloatField()),
                ('total_score', models.FloatField()),
                ('date_taken', models.DateField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_results', to='class_app.course')),
                ('professor', models.ForeignKey(limit_choices_to={'is_professor': True}, on_delete=django.db.models.deletion.CASCADE, related_name='added_results', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(limit_choices_to={'is_student': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
