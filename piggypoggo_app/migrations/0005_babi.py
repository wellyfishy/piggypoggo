# Generated by Django 5.1.5 on 2025-05-02 05:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('piggypoggo_app', '0004_kandang'),
    ]

    operations = [
        migrations.CreateModel(
            name='Babi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_babi', models.CharField(blank=True, max_length=50, null=True)),
                ('nomor_kandang', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='piggypoggo_app.kandang')),
            ],
        ),
    ]
