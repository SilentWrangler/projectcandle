# Generated by Django 3.0.8 on 2021-10-04 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0015_auto_20210916_1157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-is_current', 'priority']},
        ),
        migrations.AddField(
            model_name='project',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]
