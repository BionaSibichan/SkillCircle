
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from accounts.models import StudentProfile
from skills.models import Skill
from .models import SkillExchange



@login_required
def exchange_list(request):
    received_requests = SkillExchange.objects.filter(
        receiver=request.user
    ).select_related(
        'requester', 'receiver', 'skill'
    ).order_by('-created_at')

    sent_requests = SkillExchange.objects.filter(
        requester=request.user
    ).select_related(
        'requester', 'receiver', 'skill'
    ).order_by('-created_at')

    return render(
        request,
        'exchanges/requests.html',
        {
            'received_requests': received_requests,
            'sent_requests': sent_requests,
        }
    )


@login_required
def create_exchange(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)

    if not skill.is_offered:
        messages.error(request, 'This skill is not being offered.')
        return redirect('skills:skill_detail', skill_id=skill.id)

    if skill.user == request.user:
        messages.error(request, 'You cannot request your own skill.')
        return redirect('skills:skill_detail', skill_id=skill.id)

    if request.method == 'POST':
        already_requested = SkillExchange.objects.filter(
            requester=request.user,
            receiver=skill.user,
            skill=skill,
            status__in=['pending', 'accepted']
        ).exists()

        if already_requested:
            messages.error(
                request,
                'You already have an active request for this skill.'
            )
        else:
            exchange = SkillExchange.objects.create(
                requester=request.user,
                receiver=skill.user,
                skill=skill,
                message=request.POST.get('message', '').strip()
            )

            messages.success(request, 'Exchange request sent.')
            return redirect(
                'exchanges:request_detail',
                exchange_id=exchange.id
            )

    return render(
        request,
        'exchanges/create_exchange.html',
        {'skill': skill}
    )


@login_required
def exchange_detail(request, exchange_id):
    exchange = get_object_or_404(
        SkillExchange.objects.select_related(
            'requester', 'receiver', 'skill'
        ),
        id=exchange_id
    )

    if request.user not in (exchange.requester, exchange.receiver):
        messages.error(request, 'You cannot view this exchange.')
        return redirect('exchanges:requests')

    return render(
        request,
        'exchanges/request_detail.html',
        {'exchange_request': exchange}
    )


# Keep the existing template's URL name working.
request_detail = exchange_detail


@login_required
@require_POST
def accept_exchange(request, exchange_id):
    exchange = get_object_or_404(
        SkillExchange,
        id=exchange_id,
        receiver=request.user
    )

    if exchange.status != 'pending':
        messages.error(request, 'This request is no longer pending.')
    else:
        exchange.status = 'accepted'
        exchange.save(update_fields=['status'])
        messages.success(request, 'Exchange request accepted.')

    return redirect(
        'exchanges:request_detail',
        exchange_id=exchange.id
    )


@login_required
@require_POST
def reject_exchange(request, exchange_id):
    exchange = get_object_or_404(
        SkillExchange,
        id=exchange_id,
        receiver=request.user
    )

    if exchange.status != 'pending':
        messages.error(request, 'This request is no longer pending.')
    else:
        exchange.status = 'rejected'
        exchange.save(update_fields=['status'])
        messages.success(request, 'Exchange request rejected.')

    return redirect(
        'exchanges:request_detail',
        exchange_id=exchange.id
    )


@login_required
@require_POST
def complete_exchange(request, exchange_id):
    exchange = get_object_or_404(
        SkillExchange,
        id=exchange_id
    )

    if request.user not in (exchange.requester, exchange.receiver):
        messages.error(request, 'You cannot update this exchange.')
    elif exchange.status != 'accepted':
        messages.error(
            request,
            'Only accepted exchanges can be completed.'
        )
    else:
        exchange.status = 'completed'
        exchange.save(update_fields=['status'])
        messages.success(request, 'Exchange marked as completed.')

    return redirect(
        'exchanges:request_detail',
        exchange_id=exchange.id
    )


@login_required
def matches(request):
    matches = (
        StudentProfile.objects
        .exclude(user=request.user)
        .select_related('user')
    )

    for match in matches:
        match.offered_skills = Skill.objects.filter(
            user=match.user,
            is_offered=True
        )

    return render(
        request,
        'exchanges/matches.html',
        {'matches': matches}
    )