# Generated by Django 5.1.5 on 2025-03-17 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('piggypoggo_app', '0002_mahasiswa_matakuliah_belajar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='belajar',
            name='kd_mhs',
        ),
        migrations.RemoveField(
            model_name='belajar',
            name='kd_mkuliah',
        ),
        migrations.DeleteModel(
            name='Mahasiswa',
        ),
        migrations.DeleteModel(
            name='Belajar',
        ),
        migrations.DeleteModel(
            name='MataKuliah',
        ),
    ]
