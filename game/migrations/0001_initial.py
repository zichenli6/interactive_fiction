# Generated by Django 4.0.4 on 2022-04-24 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Name')),
                ('persona', models.TextField(verbose_name='Persona')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]
