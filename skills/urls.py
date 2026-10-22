
from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('my-skills/', views.my_skills, name='my_skills'),
    path('add/', views.add_skill, name='add_skill'),
    path('edit/<int:skill_id>/', views.edit_skill, name='edit_skill'),
    path('delete/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('<int:skill_id>/', views.skill_detail, name='skill_detail'),
]