from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_list_view, name='list'),
    path('create/', views.create_report_view, name='create'),
    path('<int:pk>/', views.report_detail_view, name='detail'),
    path('<int:pk>/resend/', views.resend_report_view, name='resend'),
    path('<int:pk>/copy/', views.copy_report_view, name='copy'),
]