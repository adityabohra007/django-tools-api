# Generated by Django 4.2.6 on 2023-10-31 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excel_reduction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='excelfile',
            name='uploaded_on',
            field=models.DateField(auto_created=True, null=True),
        ),
    ]
