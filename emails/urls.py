from django.urls import path
from . import views

app_name = 'emails'

urlpatterns = [
    path('', views.email_list_view, name='list'),
    path('add/', views.add_email_view, name='add'),
    path('<int:pk>/delete/', views.delete_email_view, name='delete'),
]