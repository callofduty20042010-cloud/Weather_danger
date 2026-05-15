from django.apps import AppConfig


class WeatherDangerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'weather_danger'

    def ready(self):
        import weather_danger.signals