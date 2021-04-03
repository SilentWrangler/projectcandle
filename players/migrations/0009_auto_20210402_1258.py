# Generated by Django 3.0.8 on 2021-04-02 09:58

from django.db import migrations, models
import players.models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0008_auto_20210402_1246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trait',
            name='static_img_file',
        ),
        migrations.AddField(
            model_name='trait',
            name='image',
            field=models.ImageField(null=True, upload_to=players.models.trait_gfx_path),
        ),
    ]
