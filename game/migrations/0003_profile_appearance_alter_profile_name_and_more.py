# Generated by Django 4.0.4 on 2022-04-24 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_profile_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='appearance',
            field=models.TextField(default='', verbose_name='Appearance'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(default='Zach Li', max_length=64, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='persona',
            field=models.TextField(default='', verbose_name='Persona'),
        ),
    ]