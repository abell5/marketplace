# Generated by Django 2.0.6 on 2018-07-05 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dssgmkt', '0017_auto_20180629_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationmembershiprequest',
            name='private_reviewer_notes',
            field=models.TextField(blank=True, help_text='Write any private comments regarding this decision. <strong>IMPORTANT: these notes are private to the organization, but all members of the organization will be able to see them.</strong>', max_length=5000, null=True, verbose_name='Private review notes'),
        ),
        migrations.AlterField(
            model_name='organizationmembershiprequest',
            name='public_reviewer_comments',
            field=models.TextField(blank=True, help_text='Write any comments you have for the applicant. <strong>IMPORTANT: These comments will be public and can be viewed by users outside ot the organization.</strong>', max_length=5000, null=True, verbose_name='Public reviewer comments'),
        ),
        migrations.AlterField(
            model_name='organizationmembershiprequest',
            name='role',
            field=models.IntegerField(choices=[(0, 'Administrator'), (1, 'Staff')], default=1, help_text='Select the role of this user in the organization. <strong>IMPORTANT: Administrators will have full permissions over the organization</strong> so only assign this permission if you are sure you want to grant this user full control of the organization.', verbose_name='User role'),
        ),
        migrations.AlterField(
            model_name='project',
            name='available_data',
            field=models.TextField(blank=True, help_text='Describe the data available to use for this project. (Size, variables, completeness, availability, privacy, etc.)', max_length=5000, null=True, verbose_name='Available data'),
        ),
        migrations.AlterField(
            model_name='project',
            name='available_staff',
            field=models.TextField(blank=True, help_text='Who from your organization would be available to provide assistance (approximately 1-3 hours per week) throughout the summer? (Technical staff, subject matter experts, etc.)', max_length=5000, null=True, verbose_name='Available staff'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_impact',
            field=models.TextField(blank=True, help_text="How critical is this project for your organization? How you're solving this problem today? What's the impact if this project is completed successfully?", max_length=5000, null=True, verbose_name='Project impact'),
        ),
        migrations.AlterField(
            model_name='project',
            name='scoping_process',
            field=models.TextField(blank=True, help_text='Describe the internal process for scoping and implementing this project (Who are the stakeholders, what discussions have already happened, etc.)', max_length=5000, null=True, verbose_name='Scoping process'),
        ),
        migrations.AlterField(
            model_name='projectlog',
            name='change_type',
            field=models.CharField(choices=[('TK', 'Task'), ('VA', 'Volunteer application'), ('ST', 'Staff')], default='TK', max_length=2),
        ),
    ]