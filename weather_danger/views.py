import json
from math import radians, sin, cos, asin, sqrt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import CommentForm, EventForm, ForecastForm, ProfileForm, SafetySignalForm, SavedLocationForm, TimelineItemForm
from .models import Comment, DangerNotification, EventForecast, EventTimelineItem, Profile, SafetySignal, SavedLocation, WeatherEvent



def _distance_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * earth_radius * asin(sqrt(a))


def _event_queryset():
    return WeatherEvent.objects.select_related('created_by').prefetch_related('comments')

def _get_user_profile(user):
    if not user.is_authenticated:
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def create_danger_notifications_for_user(user):
    profile = _get_user_profile(user)

    if not profile or profile.latitude is None or profile.longitude is None:
        return

    dangerous_events = WeatherEvent.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        status__in=['active', 'monitoring'],
        danger_level__in=['medium', 'high', 'critical'],
    )

    for event in dangerous_events:
        distance = event.distance_to_km(profile.latitude, profile.longitude)

        if distance is None:
            continue

        if distance <= 400:
            DangerNotification.objects.get_or_create(
                user=user,
                event=event,
                defaults={
                    'title': 'Опасность рядом',
                    'message': (
                        f'В радиусе примерно {round(distance, 1)} км от вас находится '
                        f'событие: “{event.title}”. Уровень опасности: {event.get_danger_level_display()}.'
                    ),
                    'distance_km': round(distance, 1),
                }
            )
        


def _event_payload(event, request=None):
    comments_count = getattr(event, 'comments_count', None)
    if comments_count is None:
        comments_count = event.comments.count()
    return {
        'id': event.id,
        'title': event.title,
        'description': event.short_description,
        'full_description': event.description,
        'event_type': event.event_type,
        'event_type_label': event.get_event_type_display(),
        'temperature': event.temperature,
        'humidity': event.humidity,
        'wind_speed': event.wind_speed,
        'latitude': event.latitude,
        'longitude': event.longitude,
        'radius_km': event.radius_km,
        'status': event.status,
        'status_label': event.get_status_display(),
        'danger_level': event.danger_level,
        'danger_label': event.get_danger_level_display(),
        'danger_color': event.danger_color,
        'credibility_score': event.credibility_score,
        'region': event.region or 'Не указан',
        'comments_count': comments_count,
        'created_at': event.created_at.strftime('%Y-%m-%d %H:%M'),
        'url': request.build_absolute_uri(event.get_absolute_url()) if request else event.get_absolute_url(),
    }


def index(request):
    if request.user.is_authenticated:
        create_danger_notifications_for_user(request.user)

    search_query = request.GET.get('search', '').strip()
    event_type = request.GET.get('type', '').strip()
    danger = request.GET.get('danger', '').strip()
    status = request.GET.get('status', '').strip()

    events = _event_queryset().annotate(comments_count=Count('comments')).order_by('-created_at')

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(region__icontains=search_query)
        )
    if event_type:
        events = events.filter(event_type=event_type)
    if danger:
        events = events.filter(danger_level=danger)
    if status:
        events = events.filter(status=status)

    stats = {
        'total': WeatherEvent.objects.count(),
        'active': WeatherEvent.objects.filter(status='active').count(),
        'critical': WeatherEvent.objects.filter(danger_level='critical').count(),
        'comments': Comment.objects.count(),
    }

    return render(request, 'index.html', {
        'events': events,
        'stats': stats,
        'event_types': WeatherEvent.EVENT_TYPES,
        'danger_levels': WeatherEvent.DANGER_LEVELS,
        'statuses': WeatherEvent.STATUSES,
    })


def safety_guide(request):
    guides = [
        {
            'icon': '🌪️', 'title': 'Пыльная буря', 'level': 'Высокая опасность для дыхания и видимости',
            'before': ['Закройте окна и двери.', 'Подготовьте маску, воду и заряженный телефон.', 'Уберите с улицы лёгкие предметы.'],
            'during': ['Оставайтесь в помещении.', 'Не садитесь за руль без крайней необходимости.', 'Закройте нос и рот маской или влажной тканью.'],
            'after': ['Проветрите помещение только после оседания пыли.', 'Проверьте детей, пожилых людей и животных.', 'Очистите фильтры и вентиляцию.'],
        },
        {
            'icon': '🌊', 'title': 'Наводнение', 'level': 'Опасность воды, тока и разрушений',
            'before': ['Соберите документы и аптечку в водонепроницаемый пакет.', 'Отключите электричество при угрозе подтопления.', 'Заранее узнайте путь к возвышенности.'],
            'during': ['Не переходите поток воды пешком или на машине.', 'Поднимитесь на верхние этажи или возвышенность.', 'Следуйте сообщениям спасательных служб.'],
            'after': ['Не включайте электричество до проверки.', 'Не пейте воду из-под крана без разрешения служб.', 'Сообщите о повреждениях и пострадавших.'],
        },
        {
            'icon': '🌎', 'title': 'Землетрясение', 'level': 'Опасность обрушений и травм',
            'before': ['Закрепите тяжёлую мебель.', 'Держите фонарик, воду и аптечку рядом.', 'Определите безопасные места в комнате.'],
            'during': ['Присядьте, укройтесь, держитесь.', 'Отойдите от окон и тяжёлых предметов.', 'Не пользуйтесь лифтом.'],
            'after': ['Проверьте травмы и запах газа.', 'Выйдите на открытое место, если здание повреждено.', 'Будьте готовы к повторным толчкам.'],
        },
        {
            'icon': '🔥', 'title': 'Пожар', 'level': 'Опасность дыма, ожогов и паники',
            'before': ['Знайте ближайшие выходы.', 'Храните огнетушитель в доступном месте.', 'Не перегружайте розетки.'],
            'during': ['Двигайтесь ниже к полу, где меньше дыма.', 'Не открывайте горячие двери.', 'Звоните 101 или 112.'],
            'after': ['Не возвращайтесь внутрь без разрешения.', 'Сообщите спасателям о пропавших людях.', 'Обратитесь к врачу при отравлении дымом.'],
        },
        {
            'icon': '⛈️', 'title': 'Гроза и сильный ветер', 'level': 'Опасность молнии, деревьев и проводов',
            'before': ['Уберите вещи с балкона.', 'Зарядите телефон и power bank.', 'Закройте окна.'],
            'during': ['Не стойте под деревьями и рекламными щитами.', 'Держитесь подальше от оборванных проводов.', 'Не используйте открытые водоёмы.'],
            'after': ['Проверьте повреждения вокруг дома.', 'Не трогайте провода.', 'Сообщите о завалах и опасных объектах.'],
        },
        {
            'icon': '🌡️', 'title': 'Экстремальная жара или мороз', 'level': 'Опасность перегрева или переохлаждения',
            'before': ['Подготовьте воду, тёплую одежду или защиту от солнца.', 'Проверьте отопление или охлаждение.', 'Следите за детьми и пожилыми людьми.'],
            'during': ['При жаре пейте воду и избегайте солнца.', 'При морозе закрывайте кожу.', 'Не игнорируйте слабость, озноб или головокружение.'],
            'after': ['Проверьте здоровье близких.', 'Пополните запасы воды и лекарств.', 'Зафиксируйте последствия в комментариях к событию.'],
        },
    ]
    return render(request, 'safety_guide.html', {'guides': guides})


@login_required(login_url='users:sign_in')
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            EventTimelineItem.objects.create(event=event, title='Событие создано', description='Первичная запись добавлена пользователем.')
            messages.success(request, 'Событие создано и добавлено на карту.')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'create_event.html', {'form': form})


@login_required(login_url='users:sign_in')
def event_detail(request, pk):
    event = get_object_or_404(_event_queryset(), pk=pk)
    comment_form = CommentForm()
    signal_form = SafetySignalForm()
    timeline_form = TimelineItemForm()
    forecast_form = ForecastForm()

    if request.method == 'POST':
        action = request.POST.get('action', 'comment')

        if action == 'comment':
            comment_form = CommentForm(request.POST, request.FILES)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.event = event
                comment.user = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен.')
                return redirect('event_detail', pk=pk)

        elif action in {'safe', 'help'}:
            SafetySignal.objects.create(
                user=request.user,
                event=event,
                signal_type=action,
                message=request.POST.get('message', ''),
                location_text=request.POST.get('location_text', ''),
                latitude=request.POST.get('latitude') or None,
                longitude=request.POST.get('longitude') or None,
            )
            if action == 'safe':
                messages.success(request, 'Статус “I am safe” сохранён.')
            else:
                messages.warning(request, 'Сигнал “Need help” сохранён. На реальном продакшене он должен уходить диспетчеру/112.')
            return redirect('event_detail', pk=pk)

        elif action == 'timeline':
            timeline_form = TimelineItemForm(request.POST)
            if timeline_form.is_valid():
                item = timeline_form.save(commit=False)
                item.event = event
                item.save()
                messages.success(request, 'Timeline обновлён.')
                return redirect('event_detail', pk=pk)

        elif action == 'forecast':
            forecast_form = ForecastForm(request.POST)
            if forecast_form.is_valid():
                forecast = forecast_form.save(commit=False)
                forecast.event = event
                forecast.save()
                messages.success(request, 'Прогноз добавлен.')
                return redirect('event_detail', pk=pk)

    comments = event.comments.select_related('user', 'user__profile')
    timeline_items = event.timeline_items.all()
    forecasts = event.forecasts.all()
    signals = event.safety_signals.select_related('user')[:8]

    return render(request, 'event_detail.html', {
        'event': event,
        'comments': comments,
        'comment_form': comment_form,
        'signal_form': signal_form,
        'timeline_form': timeline_form,
        'forecast_form': forecast_form,
        'timeline_items': timeline_items,
        'forecasts': forecasts,
        'signals': signals,
    })


@login_required(login_url='users:sign_in')
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    active_tab = request.GET.get('tab', 'passport')
    form = ProfileForm(instance=profile)
    saved_location_form = SavedLocationForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        if form_type == 'profile':
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                if form.cleaned_data.get('delete_avatar'):
                    if profile.avatar:
                        profile.avatar.delete(save=False)
                    profile.avatar = None
                profile.save()
                messages.success(request, 'Паспорт безопасности обновлён.')
                return redirect('/profile/?tab=passport')
        elif form_type == 'saved_location':
            saved_location_form = SavedLocationForm(request.POST)
            if saved_location_form.is_valid():
                loc = saved_location_form.save(commit=False)
                loc.user = request.user
                loc.save()
                messages.success(request, 'Место сохранено.')
                return redirect('/profile/?tab=locations')

    my_reports = WeatherEvent.objects.filter(created_by=request.user).annotate(comments_count=Count('comments'))
    my_comments = Comment.objects.filter(user=request.user).select_related('event')[:20]
    confirmed_events = WeatherEvent.objects.filter(credibility_score__gte=75).order_by('-created_at')[:20]
    saved_locations = SavedLocation.objects.filter(user=request.user)
    safety_signals = SafetySignal.objects.filter(user=request.user).select_related('event')[:12]

    stats = {
        'reports': my_reports.count(),
        'comments': Comment.objects.filter(user=request.user).count(),
        'saved_locations': saved_locations.count(),
        'signals': SafetySignal.objects.filter(user=request.user).count(),
    }

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form,
        'saved_location_form': saved_location_form,
        'my_reports': my_reports,
        'my_comments': my_comments,
        'confirmed_events': confirmed_events,
        'saved_locations': saved_locations,
        'safety_signals': safety_signals,
        'stats': stats,
        'active_tab': active_tab,
    })


@login_required(login_url='users:sign_in')
def events_map(request):
    create_danger_notifications_for_user(request.user)

    events = _event_queryset().annotate(comments_count=Count('comments')).filter(
        latitude__isnull=False,
        longitude__isnull=False,
    )

    events_data = [_event_payload(event, request=request) for event in events]
    stats = {
        'total': len(events_data),
        'active': sum(1 for item in events_data if item['status'] == 'active'),
        'critical': sum(1 for item in events_data if item['danger_level'] == 'critical'),
        'high': sum(1 for item in events_data if item['danger_level'] == 'high'),
    }

    return render(request, 'events_map.html', {
        'events_json': json.dumps(events_data, ensure_ascii=False),
        'event_types': WeatherEvent.EVENT_TYPES,
        'danger_levels': WeatherEvent.DANGER_LEVELS,
        'statuses': WeatherEvent.STATUSES,
        'stats': stats,
    })


def events_api(request):
    events = _event_queryset().annotate(comments_count=Count('comments')).filter(
        latitude__isnull=False,
        longitude__isnull=False,
    )
    return JsonResponse({'events': [_event_payload(event, request=request) for event in events]})


@login_required(login_url='users:sign_in')
def statistics_view(request):
    create_danger_notifications_for_user(request.user)
    
    total = WeatherEvent.objects.count()
    by_type = WeatherEvent.objects.values('event_type').annotate(count=Count('id')).order_by('-count')
    by_danger = WeatherEvent.objects.values('danger_level').annotate(count=Count('id')).order_by('-count')
    by_status = WeatherEvent.objects.values('status').annotate(count=Count('id')).order_by('-count')
    average_credibility = WeatherEvent.objects.aggregate(avg=Avg('credibility_score'))['avg'] or 0
    latest = WeatherEvent.objects.order_by('-created_at')[:8]
    event_type_labels = dict(WeatherEvent.EVENT_TYPES)
    danger_labels_dict = dict(WeatherEvent.DANGER_LEVELS)
    status_labels_dict = dict(WeatherEvent.STATUSES)
    type_labels = [event_type_labels.get(item['event_type'], item['event_type']) for item in by_type]
    type_counts = [item['count'] for item in by_type]
    danger_labels = [danger_labels_dict.get(item['danger_level'], item['danger_level']) for item in by_danger]
    danger_counts = [item['count'] for item in by_danger]
    status_labels = [status_labels_dict.get(item['status'], item['status']) for item in by_status]
    status_counts = [item['count'] for item in by_status]

    return render(request, 'statistics.html', {
        'total': total,
        'average_credibility': round(average_credibility, 1),
        'latest': latest,

        'type_labels': type_labels,
        'type_counts': type_counts,

        'danger_labels': danger_labels,
        'danger_counts': danger_counts,

        'status_labels': status_labels,
        'status_counts': status_counts,
    })

@login_required(login_url='users:sign_in')
def notifications_view(request):
    create_danger_notifications_for_user(request.user)

    notifications = DangerNotification.objects.filter(user=request.user).select_related('event')

    notifications.update(is_read=True)

    return render(request, 'notifications.html', {
        'notifications': notifications,
    })

@login_required(login_url='users:sign_in')
@require_POST
def delete_saved_location(request, pk):
    SavedLocation.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, 'Сохранённое место удалено.')
    return redirect('/profile/?tab=locations')
