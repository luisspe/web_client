# Generated by Django 4.2.7 on 2023-11-22 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0009_documento_fecha_actualizacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='tipo_documento',
            field=models.CharField(choices=[('INE_FRENTE', 'Frente de INE'), ('INE_REVERSO', 'Reverso de INE'), ('CONSTANCIA_FISCAL', 'Constancia fiscal'), ('COMPROBANTE_DOMICILIO', 'Comprobante domicilio'), ('COMPROBANTE_INGRESOS', 'Comprobante ingresos')], max_length=100),
        ),
    ]