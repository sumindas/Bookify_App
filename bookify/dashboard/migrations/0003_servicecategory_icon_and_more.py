# Generated by Django 5.1.4 on 2024-12-27 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_remove_serviceprovider_latitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicecategory",
            name="icon",
            field=models.ImageField(
                blank=True, null=True, upload_to="business_type_icons/"
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="booking_preferences",
            field=models.CharField(
                choices=[
                    ("same-day", "Same Day"),
                    ("same-day-1", "Same Day and 1 Day Before"),
                    ("same-day-2", "Same Day and 2 Days Before"),
                    ("same-day-3", "Same Day and 3 Days Before"),
                ],
                default="same-day",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="is_onboarding_complete",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="onboarding_progress",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="serviceprovider",
            name="team_size",
            field=models.IntegerField(
                default=1, help_text="Number of staff in the team."
            ),
        ),
    ]