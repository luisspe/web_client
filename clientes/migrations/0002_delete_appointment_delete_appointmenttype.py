# Generated by Django 4.2.7 on 2023-12-19 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Appointment',
        ),
        migrations.DeleteModel(
            name='AppointmentType',
        ),
    ]
