# Generated by Django 5.0 on 2023-12-27 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Administrator'), ('mod', 'Moderator'), ('user', 'Regular User')], default='user', max_length=10),
        ),
    ]
