# Generated by Django 4.2.1 on 2023-06-27 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_user_avatar_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="post_logout_redirect_uris",
            field=models.TextField(
                blank=True, help_text="Allowed Post Logout URIs list, space separated"
            ),
        ),
    ]