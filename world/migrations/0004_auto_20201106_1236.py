# Generated by Django 3.0.8 on 2020-11-06 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('world', '0003_auto_20201101_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='world',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Мир закрыт'),
        ),
    ]