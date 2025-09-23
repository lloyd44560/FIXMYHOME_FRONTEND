from trader.views.traderNotification import get_unread_notifications

def notifications_context(request):
    if request.user.is_authenticated:
        unread_qs = get_unread_notifications(request.user)
        return {
            "unread_count": unread_qs.count(),
            "unread_notifications": unread_qs[:5],  # show latest 5
        }
    return {}