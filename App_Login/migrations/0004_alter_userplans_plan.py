# Generated by Django 4.0 on 2022-01-12 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('App_Login', '0003_plans_userplans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplans',
            name='plan',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='App_Login.plans'),
        ),
    ]