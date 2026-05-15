from .models import DangerNotification


def danger_notifications(request):
    if not request.user.is_authenticated:
        return {
            'unread_notifications_count': 0,
            'popup_danger_notifications': [],
        }

    unread_notifications_count = DangerNotification.objects.filter(
        user=request.user,
        is_read=False,
    ).count()

    popup_danger_notifications = list(
        DangerNotification.objects.filter(
            user=request.user,
            shown_as_popup=False,
        ).select_related('event')[:3]
    )

    DangerNotification.objects.filter(
        id__in=[notification.id for notification in popup_danger_notifications]
    ).update(shown_as_popup=True)

    return {
        'unread_notifications_count': unread_notifications_count,
        'popup_danger_notifications': popup_danger_notifications,
    }