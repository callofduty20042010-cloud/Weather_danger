# Generated manually for the Weather Danger safety platform upgrade.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_danger', '0012_comment_location_text'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='weatherevent',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='comment_images/', verbose_name='Фото с места'),
        ),
        migrations.AddField(
            model_name='weatherevent',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weather_reports', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AddField(
            model_name='weatherevent',
            name='credibility_score',
            field=models.PositiveSmallIntegerField(default=70, help_text='Оценка достоверности события от 0 до 100.', verbose_name='Достоверность (%)'),
        ),
        migrations.AddField(
            model_name='weatherevent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='comment',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Longitude'),
        ),
        migrations.AddField(
            model_name='profile',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='profile',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='Longitude'),
        ),
        migrations.AddField(
            model_name='profile',
            name='safety_notes',
            field=models.TextField(blank=True, default='', verbose_name='Важные заметки для спасателей'),
        ),
        migrations.AlterField(
            model_name='weatherevent',
            name='danger_level',
            field=models.CharField(choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий'), ('critical', 'Критический')], max_length=10, verbose_name='Уровень опасности'),
        ),
        migrations.AlterField(
            model_name='weatherevent',
            name='event_type',
            field=models.CharField(choices=[('earthquake', 'Earthquake'), ('flood', 'Flood'), ('fire', 'Fire'), ('hurricane', 'Hurricane'), ('heavy_rain', 'Heavy Rain'), ('extreme_temp', 'Extreme Heat / Frost'), ('thunderstorm', 'Thunderstorm'), ('landslide', 'Landslide'), ('dust_storm', 'Dust Storm'), ('volcano', 'Volcano'), ('other', 'Other')], max_length=30, verbose_name='Тип явления'),
        ),
        migrations.AlterField(
            model_name='weatherevent',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('monitoring', 'Monitoring'), ('resolved', 'Resolved'), ('false_alarm', 'False Alarm')], default='active', max_length=20, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='preferred_language',
            field=models.CharField(choices=[('English', 'English'), ('Russian', 'Russian')], default='Russian', max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='timezone',
            field=models.CharField(default='Asia/Tashkent', max_length=80),
        ),
        migrations.CreateModel(
            name='EventTimelineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('happened_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline_items', to='weather_danger.weatherevent')),
            ],
            options={'ordering': ['-happened_at']},
        ),
        migrations.CreateModel(
            name='EventForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160, verbose_name='Прогноз')),
                ('details', models.TextField(blank=True, verbose_name='Детали')),
                ('trend', models.CharField(choices=[('improving', 'Улучшается'), ('stable', 'Стабильно'), ('worsening', 'Ухудшается')], default='stable', max_length=20)),
                ('expected_at', models.DateTimeField(blank=True, null=True, verbose_name='Ожидается')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forecasts', to='weather_danger.weatherevent')),
            ],
            options={'ordering': ['expected_at', '-created_at']},
        ),
        migrations.CreateModel(
            name='SavedLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location_type', models.CharField(choices=[('home', 'Home'), ('work', 'Work'), ('school', 'School'), ('family', 'Family'), ('other', 'Other')], default='other', max_length=20)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_locations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['location_type', 'name']},
        ),
        migrations.CreateModel(
            name='SafetySignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal_type', models.CharField(choices=[('safe', 'I am safe'), ('help', 'Need help')], max_length=10)),
                ('message', models.CharField(blank=True, max_length=255)),
                ('location_text', models.CharField(blank=True, max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='safety_signals', to='weather_danger.weatherevent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='safety_signals', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
