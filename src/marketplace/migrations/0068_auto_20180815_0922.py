# Generated by Django 2.0.6 on 2018-08-15 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0067_auto_20180815_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectscope',
            name='scope_analysis',
            field=models.TextField(blank=True, help_text='Describe the internal process for scoping and implementing this project (Who are the stakeholders, what discussions have already happened, etc.)', max_length=5000, null=True, verbose_name='Analysis needed'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='scope_available_data',
            field=models.TextField(blank=True, help_text='Describe the data available to use for this project. (Size, variables, completeness, availability, privacy, etc.)', max_length=5000, null=True, verbose_name='Data'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='scope_goals',
            field=models.TextField(blank=True, help_text='Describe the internal process for scoping and implementing this project (Who are the stakeholders, what discussions have already happened, etc.)', max_length=5000, null=True, verbose_name='Project goal(s)'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='scope_implementation',
            field=models.TextField(blank=True, help_text='Who from your organization would be available to provide assistance (approximately 1-3 hours per week) throughout the summer? (Technical staff, subject matter experts, etc.)', max_length=5000, null=True, verbose_name='Implementation'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='scope_interventions',
            field=models.TextField(blank=True, help_text='Describe the internal process for scoping and implementing this project (Who are the stakeholders, what discussions have already happened, etc.)', max_length=5000, null=True, verbose_name='Interventions and actions'),
        ),
        migrations.AlterField(
            model_name='projectscope',
            name='scope_validation_methodology',
            field=models.TextField(blank=True, help_text='Describe the internal process for scoping and implementing this project (Who are the stakeholders, what discussions have already happened, etc.)', max_length=5000, null=True, verbose_name='Validation methodology'),
        ),
    ]
