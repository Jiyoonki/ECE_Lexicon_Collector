# Generated by Django 3.0.8 on 2020-11-20 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenizer', '0006_auto_20201111_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_data',
            name='extra_1R',
            field=models.IntegerField(default=None, null=True),
        ),
    ]