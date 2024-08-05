# Generated by Django 5.0.7 on 2024-08-05 13:36

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chatting', '0001_initial'),
        ('users', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('chatroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatting.chatroom')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=500)),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('chatroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatting.chatroom')),
                ('mentee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.mentee')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.mentor')),
            ],
        ),
    ]
