# Generated by Django 2.2.6 on 2019-12-11 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0004_auto_20191208_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='date',
            field=models.DateField(default='2019-12-11'),
        ),
    ]
