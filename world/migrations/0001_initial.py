# Generated by Django 3.0.8 on 2020-07-23 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('main_biome', models.CharField(choices=[('WTR', 'Water'), ('PLN', 'Plain'), ('DSR', 'Desert')], max_length=3)),
                ('biome_mod', models.CharField(choices=[('NON', 'None'), ('FRT', 'Forest'), ('SWP', 'Swamp'), ('HLS', 'Hills'), ('MNT', 'Mountains')], max_length=3)),
                ('city_type', models.CharField(choices=[(None, 'No City'), ('GEN', 'Generic'), ('MAN', 'Mana'), ('FRM', 'Farm'), ('LBR', 'Library'), ('DEF', 'Fort'), ('FCT', 'Factory'), ('MIN', 'Mine'), ('SRL', 'Sorrow Lair')], max_length=3)),
                ('city_tier', models.IntegerField(default=0)),
                ('local_resource', models.CharField(choices=[(None, 'No Resource'), ('IRN', 'Iron'), ('GLD', 'Gold'), ('SVR', 'Silver'), ('ALM', 'Aluminium'), ('QRZ', 'Quartz'), ('DMD', 'Diamonds'), ('RBY', 'Rubies'), ('SPH', 'Saphires'), ('ABR', 'Amber'), ('EMR', 'Emerald'), ('AMT', 'Amethists'), ('OBS', 'Obsidian'), ('WYV', 'Wyverns'), ('HRS', 'Horses')], max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Pop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race', models.CharField(choices=[('HUM', 'Human'), ('ELF', 'Elf'), ('ORC', 'Orc'), ('DWA', 'Dwarf'), ('GOB', 'Goblin'), ('FEY', 'Fey')], max_length=3)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.Cell')),
            ],
        ),
        migrations.CreateModel(
            name='World',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(verbose_name='Мир запущен')),
                ('end_date', models.DateTimeField(verbose_name='Мир закрыт')),
                ('end_type', models.CharField(choices=[('LS', 'Мир уничтожен'), ('WN', 'Мир спасён'), ('NY', 'Исход не решён')], default='NY', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='PopTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('content', models.CharField(max_length=100)),
                ('pop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.Pop')),
            ],
        ),
        migrations.CreateModel(
            name='CellTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('content', models.CharField(max_length=100)),
                ('cell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.Cell')),
            ],
        ),
        migrations.AddField(
            model_name='cell',
            name='world',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='world.World'),
        ),
    ]
