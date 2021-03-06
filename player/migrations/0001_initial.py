# Generated by Django 2.1.1 on 2018-11-06 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money_type', models.CharField(choices=[('EUR', 'EUR'), ('BNS', 'Bonus Money')], default='BNS', max_length=3)),
                ('is_active', models.BooleanField(default=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16)),
                ('event', models.CharField(choices=[('FIRST_LOGIN', 'First log in'), ('DEPOSIT', 'Deposit')], default='LOGIN', max_length=10)),
                ('deposit_min_value', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('wagering_requirement', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_login_bonus_used', models.BooleanField(default=False, verbose_name='Login bonus used')),
                ('money_wagered', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WageringRequirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('bonus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Bonus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_depleted', models.BooleanField(default=False)),
                ('money_type', models.CharField(choices=[('EUR', 'EUR'), ('BNS', 'Bonus Money')], default='BNS', max_length=3)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('spin_priority', models.IntegerField(default=1)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='wageringrequirement',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Wallet'),
        ),
    ]
