# Generated by Django 4.2.1 on 2023-05-31 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_item_instance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Completed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output', models.CharField(max_length=1999)),
            ],
        ),
        migrations.RemoveField(
            model_name='item',
            name='type',
        ),
    ]
