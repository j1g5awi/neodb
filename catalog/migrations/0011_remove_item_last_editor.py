# Generated by Django 4.2.4 on 2023-08-11 20:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0010_alter_item_polymorphic_ctype"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="item",
            name="last_editor",
        ),
    ]
