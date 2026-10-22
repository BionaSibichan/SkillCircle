
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date

from exchanges.models import SkillExchange
from .models import LearningSession


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

    if request.user not in (exchange.requester, exchange.receiver):
        messages.error(request, 'You cannot schedule this session.')
        return redirect('exchanges:exchange_list')

    if exchange.status != 'accepted':
        messages.error(
            request, 'Only accepted exchanges can be scheduled.'
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

        meeting_link = request.POST.get('meeting_link', '').strip()
        notes = request.POST.get('notes', '').strip()

        if (
            session_date is None
            or start_time is None
            or end_time is None
            or session_date < date.today()
            or end_time <= start_time
        ):
            messages.error(
                request,
                'Enter a valid date and time. The end time must '
                'be after the start time.'
            )
        else:
            session = LearningSession.objects.create(
                exchange=exchange,
                teacher=exchange.receiver,
                learner=exchange.requester,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                meeting_link=meeting_link,
                notes=notes
            )

            messages.success(request, 'Learning session scheduled.')
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
