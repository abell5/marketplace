# Generated by Django 2.0.6 on 2018-07-23 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0048_auto_20180722_2039'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignupCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A code that users can type when signing up in the site that will grant them benefits.', max_length=50, verbose_name='Signup code')),
                ('type', models.IntegerField(choices=[(0, 'Automatically accept user as volunteer')], default=0)),
                ('expiration_date', models.DateField(blank=True, help_text='Expiration date after which the code will no longer valid', null=True, verbose_name='Expiration date')),
                ('max_uses', models.IntegerField(blank=True, help_text='Maximum number of users that can use this code, if any.', null=True, verbose_name='Maximum number of uses')),
                ('current_uses', models.IntegerField(blank=True, help_text='Number of times this code has been used.', null=True, verbose_name='Times used')),
            ],
        ),
    ]
