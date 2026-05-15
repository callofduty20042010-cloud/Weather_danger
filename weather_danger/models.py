from math import radians, sin, cos, asin, sqrt

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class WeatherEvent(models.Model):
    EVENT_TYPES = [
        ('earthquake', 'Earthquake'),
        ('flood', 'Flood'),
        ('fire', 'Fire'),
        ('hurricane', 'Hurricane'),
        ('heavy_rain', 'Heavy Rain'),
        ('extreme_temp', 'Extreme Heat / Frost'),
        ('thunderstorm', 'Thunderstorm'),
        ('landslide', 'Landslide'),
        ('dust_storm', 'Dust Storm'),
        ('volcano', 'Volcano'),
        ('other', 'Other'),
    ]

    DANGER_LEVELS = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]

    STATUSES = [
        ('active', 'Active'),
        ('monitoring', 'Monitoring'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weather_reports',
        verbose_name='Автор'
    )

    wind_speed = models.FloatField(verbose_name='Скорость ветра (м/с)', null=True, blank=True)
    humidity = models.IntegerField(verbose_name='Влажность (%)', null=True, blank=True)
    temperature = models.FloatField(verbose_name='Температура (°C)', null=True, blank=True)
    region = models.CharField(max_length=100, verbose_name='Регион', blank=True)

    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name='Тип явления')
    danger_level = models.CharField(max_length=10, choices=DANGER_LEVELS, verbose_name='Уровень опасности')
    status = models.CharField(max_length=20, choices=STATUSES, verbose_name='Статус', default='active')
    radius_km = models.PositiveIntegerField(verbose_name='Радиус опасности (км)', default=1)
    credibility_score = models.PositiveSmallIntegerField(
        verbose_name='Достоверность (%)',
        default=70,
        help_text='Оценка достоверности события от 0 до 100.'
    )

    latitude = models.FloatField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Longitude', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', args=[self.pk])

    @property
    def danger_weight(self):
        return {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(self.danger_level, 1)

    @property
    def danger_color(self):
        return {
            'low': '#27d17f',
            'medium': '#ffd166',
            'high': '#ff8c42',
            'critical': '#ff3b5c',
        }.get(self.danger_level, '#9d7bff')

    @property
    def short_description(self):
        text = (self.description or '').strip()
        return text if len(text) <= 110 else text[:107] + '...'

    def distance_to_km(self, latitude, longitude):
        if self.latitude is None or self.longitude is None or latitude is None or longitude is None:
            return None
        earth_radius = 6371
        lat1, lon1, lat2, lon2 = map(radians, [self.latitude, self.longitude, latitude, longitude])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * earth_radius * asin(sqrt(a))


class Comment(models.Model):
    event = models.ForeignKey(WeatherEvent, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Комментарий')
    image = models.ImageField(upload_to='comment_images/', blank=True, null=True, verbose_name='Фото с места')
    location_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Моя геолокация',
        help_text='Например: 41.3111, 69.2797'
    )
    latitude = models.FloatField(verbose_name='Latitude', null=True, blank=True)
    longitude = models.FloatField(verbose_name='Longitude', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий от {self.user} к {self.event}'


class EventTimelineItem(models.Model):
    event = models.ForeignKey(WeatherEvent, on_delete=models.CASCADE, related_name='timeline_items')
    title = models.CharField(max_length=160, verbose_name='Заголовок')
    description = models.TextField(blank=True, verbose_name='Описание')
    happened_at = models.DateTimeField(default=timezone.now, verbose_name='Время')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-happened_at']

    def __str__(self):
        return f'{self.event}: {self.title}'


class EventForecast(models.Model):
    TREND_CHOICES = [
        ('improving', 'Улучшается'),
        ('stable', 'Стабильно'),
        ('worsening', 'Ухудшается'),
    ]

    event = models.ForeignKey(WeatherEvent, on_delete=models.CASCADE, related_name='forecasts')
    title = models.CharField(max_length=160, verbose_name='Прогноз')
    details = models.TextField(blank=True, verbose_name='Детали')
    trend = models.CharField(max_length=20, choices=TREND_CHOICES, default='stable')
    expected_at = models.DateTimeField(null=True, blank=True, verbose_name='Ожидается')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expected_at', '-created_at']

    def __str__(self):
        return f'{self.event}: {self.title}'


class SavedLocation(models.Model):
    LOCATION_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('school', 'School'),
        ('family', 'Family'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_locations')
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='other')
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['location_type', 'name']

    def __str__(self):
        return f'{self.user}: {self.name}'


class SafetySignal(models.Model):
    SIGNAL_TYPES = [
        ('safe', 'I am safe'),
        ('help', 'Need help'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='safety_signals')
    event = models.ForeignKey(WeatherEvent, on_delete=models.CASCADE, related_name='safety_signals', null=True, blank=True)
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPES)
    message = models.CharField(max_length=255, blank=True)
    location_text = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user}: {self.get_signal_type_display()}'


class Profile(models.Model):
    GENDER_CHOICES = [
        ('', 'Select gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    BLOOD_TYPE_CHOICES = [
        ('', 'Select blood type'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Russian', 'Russian'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)

    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True, verbose_name='Latitude')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Longitude')

    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True)
    medical_conditions = models.CharField(max_length=255, blank=True)
    safety_notes = models.TextField(blank=True, default='', verbose_name='Важные заметки для спасателей')

    preferred_language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='Russian')
    timezone = models.CharField(max_length=80, default='Asia/Tashkent')
    occupation = models.CharField(max_length=120, blank=True)
    organization = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.user.username

class DangerNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='danger_notifications',
        verbose_name='Пользователь'
    )
    event = models.ForeignKey(
        WeatherEvent,
        on_delete=models.CASCADE,
        related_name='danger_notifications',
        verbose_name='Катаклизм'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    distance_km = models.FloatField(verbose_name='Расстояние, км')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    shown_as_popup = models.BooleanField(default=False, verbose_name='Показано всплывающим окном')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'event')
        verbose_name = 'Уведомление об опасности'
        verbose_name_plural = 'Уведомления об опасности'

    def __str__(self):
        return f'{self.user} — {self.event}'