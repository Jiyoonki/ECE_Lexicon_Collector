# Generated by Django 3.0.8 on 2020-08-19 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tokenizer', '0002_auto_20200814_2213'),
    ]

    operations = [
        migrations.CreateModel(
            name='progress_state',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tokenizer.keyword_select',),
        ),
    ]