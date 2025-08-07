from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Lista de relatórios
    path('', views.relatorios_list, name='list'),
    
    # Criar novo relatório
    path('novo/', views.relatorio_create, name='create'),
    
    # Visualizar relatório
    path('<int:pk>/', views.relatorio_detail, name='detail'),
    
    # Editar relatório
    path('<int:pk>/editar/', views.relatorio_edit, name='edit'),
    
    # Deletar relatório
    path('<int:pk>/deletar/', views.relatorio_delete, name='delete'),
]