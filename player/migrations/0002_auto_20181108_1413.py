# Generated by Django 2.1 on 2018-11-08 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='event',
            field=models.CharField(choices=[('FIRST_LOGIN', 'First log in'), ('DEPOSIT', 'Deposit')], default='FIRST_LOGIN', max_length=20),
        ),
    ]
