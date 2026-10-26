
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User
from .models import Skill


@login_required
def skill_list(request):
    query = request.GET.get('q', '').strip()

    offered_skills = Skill.objects.filter(is_offered=True)

    users = User.objects.exclude(
        id=request.user.id
    ).prefetch_related(
        Prefetch(
            'skills',
            queryset=offered_skills,
            to_attr='offered_skills'
        )
    )

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(skills__skill_name__icontains=query)
            | Q(skills__description__icontains=query)
        ).distinct()

    matches = []

    for user in users:
        user.offered_skill = (
            user.offered_skills[0].skill_name
            if user.offered_skills else ''
        )
        matches.append(user)

    return render(request, 'skills/skill_list.html', {
        'matches': matches,
        'query': query,
    })



@login_required
def add_skill(request):
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        category = request.POST.get('category', '').strip()
        description = request.POST.get('description', '').strip()
        is_offered = request.POST.get('is_offered', 'true') == 'true'

        valid_categories = [
            choice[0] for choice in Skill.CATEGORY_CHOICES
        ]

        if not skill_name or category not in valid_categories:
            messages.error(
                request,
                'Enter a skill name and valid category.'
            )
        else:
            Skill.objects.create(
                user=request.user,
                skill_name=skill_name,
                category=category,
                description=description,
                is_offered=is_offered
            )

            messages.success(request, 'Skill added successfully.')
            return redirect('skills:my_skills')

    return render(
        request,
        'skills/add_skill.html',
        {
            'category_choices': Skill.CATEGORY_CHOICES
        }
    )


@login_required
def skill_detail(request, skill_id):
    skill = get_object_or_404(
        Skill.objects.select_related('user'),
        id=skill_id
    )

    return render(
        request,
        'skills/skill_detail.html',
        {'skill': skill}
    )


@login_required
def edit_skill(request, skill_id):
    skill = get_object_or_404(
        Skill, id=skill_id, user=request.user
    )

    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        category = request.POST.get('category', '')
        description = request.POST.get('description', '').strip()
        is_offered = request.POST.get('is_offered', 'true').lower() in [
    'on', 'true', '1', 'yes'
]

        valid_categories = [
            choice[0] for choice in Skill.CATEGORY_CHOICES
        ]

        if not skill_name or category not in valid_categories:
            messages.error(request, 'Enter a skill name and valid category.')
        else:
            skill.skill_name = skill_name
            skill.category = category
            skill.description = description
            skill.is_offered = is_offered
            skill.save()

            messages.success(request, 'Skill updated successfully.')
            return redirect('skills:skill_list')

    return render(
        request,
        'skills/edit_skill.html',
        {'skill': skill}
    )


@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(
        Skill, id=skill_id, user=request.user
    )

    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted successfully.')
        return redirect('skills:skill_list')

    return render(
        request,
        'skills/confirm_delete.html',
        {'skill': skill}
    )

@login_required
def my_skills(request):
    my_skills = Skill.objects.filter(user=request.user)

    offered_skills = my_skills.filter(is_offered=True)
    wanted_skills = my_skills.filter(is_offered=False)

    return render(
        request,
        'skills/my_skills.html',
        {
            'offered_skills': offered_skills,
            'wanted_skills': wanted_skills,
        }
    )