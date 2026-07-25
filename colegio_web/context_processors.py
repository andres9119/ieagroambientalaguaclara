from usuarios.models import Notificacion

def internal_notifications(request):
    if request.user.is_authenticated:
        notifs = Notificacion.objects.filter(usuario=request.user)
        unread_count = notifs.filter(leido=False).count()
        return {
            'internal_notifications': notifs,
            'unread_notifications_count': unread_count
        }
    return {
        'internal_notifications': [],
        'unread_notifications_count': 0
    }
