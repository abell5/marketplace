# Generated by Django 2.0.6 on 2018-06-13 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_auto_20180607_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('DR', 'Draft'), ('NW', 'New'), ('DE', 'In scoping phase'), ('DA', 'Waiting for design review'), ('WS', 'Waiting for volunteers'), ('IP', 'In progress'), ('WR', 'Waiting review'), ('CO', 'Completed'), ('EX', 'Expired'), ('RM', 'Deleted')], default='DR', max_length=2),
        ),
        migrations.AlterField(
            model_name='projecttask',
            name='stage',
            field=models.CharField(choices=[('NOT', 'Not started'), ('AVL', 'Accepting volunteers'), ('STA', 'Started'), ('PRW', 'Pending review'), ('COM', 'Completed'), ('DEL', 'Deleted')], default='NOT', max_length=3),
        ),
        migrations.AlterUniqueTogether(
            name='projectfollower',
            unique_together={('user', 'project')},
        ),
        migrations.AlterUniqueTogether(
            name='projectrole',
            unique_together={('user', 'project')},
        ),
        migrations.AlterUniqueTogether(
            name='projecttaskrole',
            unique_together={('user', 'task')},
        ),
        migrations.AlterUniqueTogether(
            name='skill',
            unique_together={('area', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='volunteerskill',
            unique_together={('user', 'skill')},
        ),
    ]
