
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    user_notifications = Notification.objects.filter(
        recipient=request.user
    )

    return render(
        request,
        'notifications/notification_list.html',
        {'notifications': user_notifications}
    )


@login_required
@require_POST
def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect('notifications:list')
