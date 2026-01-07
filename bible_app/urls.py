from django.urls import path
from . import views

app_name = 'bible_app'

urlpatterns = [
    path('', views.chartboard, name='chartboard'),
    path('api/get_verse/', views.get_verse_api, name='get_verse_api'),
]
