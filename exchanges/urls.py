
from django.urls import path
from . import views

app_name = 'exchanges'

urlpatterns = [
    path('', views.exchange_list, name='exchange_list'),
    path('requests/', views.exchange_list, name='requests'),

    path(
        'create/<int:skill_id>/',
        views.create_exchange,
        name='create_exchange'
    ),

    path(
        '<int:exchange_id>/',
        views.exchange_detail,
        name='exchange_detail'
    ),
    path(
        '<int:exchange_id>/detail/',
        views.request_detail,
        name='request_detail'
    ),

    path(
        '<int:exchange_id>/accept/',
        views.accept_exchange,
        name='accept_exchange'
    ),
    path(
        '<int:exchange_id>/reject/',
        views.reject_exchange,
        name='reject_exchange'
    ),
    path(
        '<int:exchange_id>/complete/',
        views.complete_exchange,
        name='complete_exchange'
    ),
    path('matches/', views.matches, name='matches'),
]
