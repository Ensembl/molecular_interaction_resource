# Generated by Django 4.0 on 2022-09-27 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourcedb',
            name='label',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
