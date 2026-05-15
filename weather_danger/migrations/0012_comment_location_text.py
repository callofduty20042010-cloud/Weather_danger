from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_danger', '0011_alter_weatherevent_region_alter_comment_event_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='location_text',
            field=models.CharField(
                blank=True,
                help_text='Например: Ташкент, Чиланзар или 41.3111, 69.2797',
                max_length=255,
                verbose_name='Моя геолокация'
            ),
        ),
    ]
