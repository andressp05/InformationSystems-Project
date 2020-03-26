# Generated by Django 2.2.7 on 2019-12-17 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='medico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreM', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='paciente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreP', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='receta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplicacion.medico')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplicacion.paciente')),
            ],
        ),
    ]
