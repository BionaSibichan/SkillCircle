
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from skills.models import Skill
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created!')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard:dashboard')
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )




def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have logged out.')
        return redirect('accounts:login')

    return redirect('dashboard:dashboard')



@login_required
def profile(request):
    student_profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name()
                         or request.user.username,
            'department': '',
            'year_of_study': 1
        }
    )

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        department = request.POST.get('department', '').strip()
        year = request.POST.get('year_of_study', '')

        try:
            year = int(year)

            if not full_name or year < 1:
                raise ValueError

            student_profile.full_name = full_name
            student_profile.department = department
            student_profile.year_of_study = year

            if request.FILES.get('profile_picture'):
                student_profile.profile_picture = request.FILES[
                    'profile_picture'
                ]

            student_profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')

        except ValueError:
            messages.error(request, 'Enter valid profile details.')

    # Fetch the logged-in user's skills
    offered_skills = Skill.objects.filter(
        user=request.user,
        is_offered=True
    ).order_by('-created_at')

    wanted_skills = Skill.objects.filter(
        user=request.user,
        is_offered=False
    ).order_by('-created_at')

    return render(
        request,
        'accounts/profile.html',
        {
            'student_profile': student_profile,
            'offered_skills': offered_skills,
            'wanted_skills': wanted_skills,
        }
    )


@login_required
def edit_profile(request):
    student_profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name()
                         or request.user.username,
            'department': '',
            'year_of_study': 1
        }
    )

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        department = request.POST.get('department', '').strip()
        year = request.POST.get('year_of_study', '')

        try:
            year = int(year)

            if not full_name or year < 1:
                raise ValueError

            if not email:
                messages.error(request, 'Email address is required.')
                return redirect('accounts:edit_profile')

            validate_email(email)

            student_profile.full_name = full_name
            student_profile.department = department
            student_profile.year_of_study = year

            if request.FILES.get('profile_picture'):
                student_profile.profile_picture = request.FILES[
                    'profile_picture'
                ]

            student_profile.save()

            # Update the Django User account
            name_parts = full_name.split(maxsplit=1)
            request.user.first_name = name_parts[0]
            request.user.last_name = (
                name_parts[1] if len(name_parts) > 1 else ''
            )
            request.user.email = email
            request.user.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')

        except ValueError:
            messages.error(request, 'Enter valid profile details.')
        except ValidationError:
            messages.error(request, 'Enter a valid email address.')

    return render(
        request,
        'accounts/edit_profile.html',
        {'student_profile': student_profile}
    )
