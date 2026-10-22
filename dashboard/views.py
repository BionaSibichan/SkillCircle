
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from skills.models import Skill
from exchanges.models import SkillExchange
from learning_sessions.models import LearningSession
from .models import Notification


@login_required
def dashboard(request):
    user = request.user

    # Get the logged-in student's skills
    my_skills = Skill.objects.filter(user=user)

    # Get exchanges sent or received by the student
    my_exchanges = SkillExchange.objects.filter(
        Q(requester=user) | Q(receiver=user)
    ).select_related('requester', 'receiver', 'skill').distinct()

    # Get the student's learning sessions
    my_sessions = LearningSession.objects.filter(
        Q(teacher=user) | Q(learner=user)
    ).select_related(
        'teacher', 'learner', 'exchange', 'exchange__skill'
    ).distinct().order_by('session_date', 'start_time')

    # Get unread notifications
    unread_count = Notification.objects.filter(
        user=user,
        is_read=False
    ).count()

    context = {
        'my_skills': my_skills,
        'my_exchanges': my_exchanges,
        'my_sessions': my_sessions,
        'unread_count': unread_count,
        'skills_count': my_skills.count(),
        'pending_count': my_exchanges.filter(
            status='pending'
        ).count(),
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    if request.method == 'POST':
        user_notifications.filter(
            is_read=False
        ).update(is_read=True)

        messages.success(
            request,
            'All notifications marked as read.'
        )

        return redirect('dashboard:notifications')

    return render(
        request,
        'dashboard/notifications.html',
        {'notifications': user_notifications}
    )
