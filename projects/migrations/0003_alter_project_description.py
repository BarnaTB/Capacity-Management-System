# Generated by Django 4.1.7 on 2023-05-10 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_end_date_alter_project_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(max_length=150),
        ),
    ]
