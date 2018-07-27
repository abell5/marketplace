# Generated by Django 2.0.6 on 2018-07-27 16:19

from django.db import migrations, models
import dssgmkt.models.user


class Migration(migrations.Migration):

    dependencies = [
        ('dssgmkt', '0060_auto_20180724_1652'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', dssgmkt.models.user.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(help_text='Type the name of your organization.', max_length=200, verbose_name='Organization name'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='phone_number',
            field=models.CharField(blank=True, max_length=17, null=True, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text='Name of this project. Make sure it is distinctive and recognizable on its own.', max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=17, null=True, verbose_name='Phone number'),
        ),
    ]
