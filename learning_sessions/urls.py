
from django.urls import path
from . import views


app_name = 'learning_sessions'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('schedule/<int:exchange_id>/', views.schedule_session, name='schedule_session'),
    path('edit/<int:session_id>/', views.edit_session, name='edit_session'),
    path('cancel/<int:session_id>/', views.cancel_session, name='cancel_session'),
    path('complete/<int:session_id>/', views.complete_session, name='complete_session'),
]
