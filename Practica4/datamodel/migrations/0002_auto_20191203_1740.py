# Generated by Django 2.1.7 on 2019-12-03 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='date',
            field=models.DateField(default='2019-12-03'),
        ),
    ]
