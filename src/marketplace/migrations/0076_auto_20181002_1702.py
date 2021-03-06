# Generated by Django 2.0.6 on 2018-10-02 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0075_rename_dummy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='email_address',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Contact email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
