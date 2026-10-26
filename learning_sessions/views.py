
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date
from django.db import models
from exchanges.models import SkillExchange
from .models import LearningSession
from django.utils import timezone
from django.db import transaction
from notifications.models import Notification

@login_required
def session_list(request):
    sessions = LearningSession.objects.filter(
        Q(teacher=request.user) | Q(learner=request.user)
    ).select_related(
        'teacher', 'learner', 'exchange', 'exchange__skill'
    ).order_by('session_date', 'start_time')

    return render(
        request,
        'learning_sessions/session_list.html',
        {'sessions': sessions}
    )



@login_required
def schedule_session(request, exchange_id):
    exchange = get_object_or_404(
        SkillExchange.objects.select_related(
            'requester', 'receiver', 'skill'
        ),
        id=exchange_id
    )

    # Check whether the logged-in user belongs to this exchange.
    if request.user not in (exchange.requester, exchange.receiver):
        messages.error(request, 'You cannot schedule this session.')
        return redirect('exchanges:exchange_list')

    # Only accepted exchanges can be scheduled.
    if exchange.status != 'accepted':
        messages.error(
            request,
            'Only accepted exchanges can be scheduled.'
        )
        return redirect(
            'exchanges:exchange_detail',
            exchange_id=exchange.id
        )

    if request.method == 'POST':
        session_date = parse_date(
            request.POST.get('session_date', '')
        )
        start_time = parse_time(
            request.POST.get('start_time', '')
        )
        end_time = parse_time(
            request.POST.get('end_time', '')
        )

        meeting_link = request.POST.get(
            'meeting_link', ''
        ).strip()
        notes = request.POST.get('notes', '').strip()
        reminder_enabled = (
            request.POST.get('reminder_enabled') == 'on'
        )

        errors = []

        # Validate the date and times.
        if not session_date or not start_time or not end_time:
            errors.append('Enter a valid date and time.')
        else:
            today = timezone.localdate()

            if session_date < today:
                errors.append(
                    'The session date cannot be in the past.'
                )

            if end_time <= start_time:
                errors.append(
                    'End time must be after start time.'
                )

            if session_date == today:
                start_datetime = timezone.make_aware(
                    timezone.datetime.combine(
                        session_date, start_time
                    ),
                    timezone.get_current_timezone()
                )

                if start_datetime <= timezone.now():
                    errors.append(
                        'Choose a future start time.'
                    )

        # Validate the meeting URL, if supplied.
        if meeting_link:
            from urllib.parse import urlparse

            parsed_link = urlparse(meeting_link)

            if (
                parsed_link.scheme not in ('http', 'https')
                or not parsed_link.netloc
            ):
                errors.append(
                    'Enter a valid online meeting URL.'
                )

        if errors:
            for error in errors:
                messages.error(request, error)

        else:
            # Check whether either participant already has
            # another session during this time.
            participants = [
                exchange.receiver,
                exchange.requester,
            ]

            conflicts = LearningSession.objects.filter(
                session_date=session_date,
                is_completed=False,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).filter(
                Q(teacher__in=participants)
                | Q(learner__in=participants)
            )

            if conflicts.exists():
                messages.error(
                    request,
                    'A participant already has a session '
                    'at that time. Please choose another time.'
                )

            else:
                # Create the session and notification together.
                with transaction.atomic():
                    session = LearningSession.objects.create(
                        exchange=exchange,
                        teacher=exchange.receiver,
                        learner=exchange.requester,
                        session_date=session_date,
                        start_time=start_time,
                        end_time=end_time,
                        meeting_link=meeting_link,
                        notes=notes,
                        reminder_enabled=reminder_enabled,
                    )

                    # Notify the other participant.
                    if request.user == exchange.receiver:
                        recipient = exchange.requester
                    else:
                        recipient = exchange.receiver

                    Notification.objects.create(
                        recipient=recipient,
                        title='New Learning Session Scheduled',
                        message=(
                            f"{request.user.username} scheduled a "
                            f"learning session for "
                            f"{exchange.skill.skill_name} on "
                            f"{session_date.strftime('%B %d, %Y')} "
                            f"from {start_time.strftime('%I:%M %p')} "
                            f"to {end_time.strftime('%I:%M %p')}."
                        )
                    )

                messages.success(
                    request,
                    'Learning session scheduled successfully.'
                )

                return redirect(
                    'learning_sessions:session_list'
                )

    return render(
        request,
        'learning_sessions/schedule_session.html',
        {'exchange': exchange}
    )



@login_required
def edit_session(request, session_id):
    session = get_object_or_404(
        LearningSession, id=session_id
    )

    if request.user not in (session.teacher, session.learner):
        messages.error(request, 'You cannot edit this session.')
        return redirect('learning_sessions:session_list')

    if request.method == 'POST':
        session_date = parse_date(
            request.POST.get('session_date', '')
        )
        start_time = parse_time(
            request.POST.get('start_time', '')
        )
        end_time = parse_time(
            request.POST.get('end_time', '')
        )

        if (
            session_date is None
            or start_time is None
            or end_time is None
            or session_date < date.today()
            or end_time <= start_time
        ):
            messages.error(request, 'Enter a valid date and time.')
        else:
            session.session_date = session_date
            session.start_time = start_time
            session.end_time = end_time
            session.meeting_link = request.POST.get(
                'meeting_link', ''
            ).strip()
            session.notes = request.POST.get('notes', '').strip()
            session.save()

            messages.success(request, 'Session updated.')
            return redirect('learning_sessions:session_list')

    return render(
        request,
        'learning_sessions/edit_session.html',
        {'session': session}
    )


@login_required
@require_POST
def cancel_session(request, session_id):
    session = get_object_or_404(
        LearningSession, id=session_id
    )

    if request.user not in (session.teacher, session.learner):
        messages.error(request, 'You cannot cancel this session.')
    else:
        session.delete()
        messages.success(request, 'Session cancelled.')

    return redirect('learning_sessions:session_list')


@login_required
@require_POST
def complete_session(request, session_id):
    session = get_object_or_404(
        LearningSession, id=session_id
    )

    if request.user not in (session.teacher, session.learner):
        messages.error(request, 'You cannot update this session.')
    else:
        session.is_completed = True
        session.save(update_fields=['is_completed'])
        messages.success(request, 'Session marked as completed.')

    return redirect('learning_sessions:session_list')
