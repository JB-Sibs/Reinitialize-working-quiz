# Generated by Django 4.2.16 on 2024-10-13 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class_app', '0010_examresult_period_grade_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='Is admin'),
        ),
    ]
