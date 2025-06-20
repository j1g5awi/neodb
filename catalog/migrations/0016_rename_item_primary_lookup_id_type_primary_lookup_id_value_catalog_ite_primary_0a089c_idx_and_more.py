# Generated by Django 4.2.21 on 2025-05-21 04:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0015_item_add_is_protected"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="item",
            new_name="catalog_ite_primary_0a089c_idx",
            old_fields=("primary_lookup_id_type", "primary_lookup_id_value"),
        ),
        migrations.RenameIndex(
            model_name="podcastepisode",
            new_name="catalog_pod_program_2e4327_idx",
            old_fields=("program", "pub_date"),
        ),
    ]
