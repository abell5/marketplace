# Generated by Django 2.0.6 on 2018-07-13 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0029_auto_20180713_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectscope',
            name='scope',
            field=models.TextField(blank=True, help_text='The detailed scope of the project.', max_length=5000, null=True, verbose_name='Project scope'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='version_notes',
            field=models.TextField(default='No changes provided.', help_text='Type the reason the scope is being modified and describe the changes made.', max_length=5000, verbose_name='New version notes'),
            preserve_default=False,
        ),
    ]
