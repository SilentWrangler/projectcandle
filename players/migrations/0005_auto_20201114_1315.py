# Generated by Django 3.0.8 on 2020-11-14 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0004_auto_20201114_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trait',
            name='name',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]