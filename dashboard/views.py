
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from skills.models import Skill
from exchanges.models import SkillExchange
from learning_sessions.models import LearningSession
from django.utils import timezone
from notifications.models import Notification
@login_required
def dashboard(request):
    # Count skills the current user offers to teach
    offered_count = Skill.objects.filter(
        user=request.user,
        is_offered=True
    ).count()

    # Count skills the current user wants to learn
    wanted_count = Skill.objects.filter(
        user=request.user,
        is_offered=False
    ).count()

    # Count incoming pending exchange requests
    pending_count = SkillExchange.objects.filter(
        receiver=request.user,
        status='pending'
    ).count()

    # Get sessions where the user is the teacher or learner
    user_sessions = LearningSession.objects.filter(
        teacher=request.user
    ) | LearningSession.objects.filter(
        learner=request.user
    )

    session_count = user_sessions.count()

    # Get upcoming, incomplete sessions
    today = timezone.localdate()

    upcoming_sessions = user_sessions.filter(
        session_date__gte=today,
        is_completed=False
    ).order_by('session_date', 'start_time')[:5]

    context = {
        'offered_count': offered_count,
        'wanted_count': wanted_count,
        'pending_count': pending_count,
        'session_count': session_count,
        'upcoming_sessions': upcoming_sessions,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )

@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    return render(
        request,
        'notifications/notification_list.html',
        {'notifications': user_notifications}
    )

