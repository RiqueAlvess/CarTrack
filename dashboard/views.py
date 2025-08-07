from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict

from reports.models import Report
from django.contrib.auth import get_user_model

User = get_user_model()


def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


@login_required
def dashboard_view(request):
    """Dashboard individual do usuário"""
    user = request.user
    now = timezone.now()
    
    # Filtros de tempo
    today = now.date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    last_7_days = today - timedelta(days=7)
    
    # Relatórios do usuário
    user_reports = Report.objects.filter(user=user)
    
    # Estatísticas básicas
    stats = {
        'total_reports': user_reports.count(),
        'reports_this_month': user_reports.filter(created_at__date__gte=this_month_start).count(),
        'reports_sent': user_reports.filter(email_status='sent').count(),
        'reports_today': user_reports.filter(created_at__date=today).count(),
    }
    
    # Totais acumulados
    totals = user_reports.aggregate(
        total_cars_cleaned=Sum('total_cleaned'),
        total_forecasted_drops=Sum('forecasted_drops'),
        avg_cars_per_report=Avg('total_cleaned'),
    )
    
    # Dados dos últimos 7 dias para gráficos
    daily_data = []
    drops_data = []
    
    for i in range(7):
        date = today - timedelta(days=6-i)
        day_reports = user_reports.filter(created_at__date=date)
        
        daily_cars = day_reports.aggregate(total=Sum('total_cleaned'))['total'] or 0
        daily_drops = day_reports.aggregate(total=Sum('forecasted_drops'))['total'] or 0
        
        daily_data.append({
            'date': date.strftime('%d/%m'),
            'day': date.strftime('%a'),
            'cars': daily_cars,
        })
        
        drops_data.append({
            'date': date.strftime('%d/%m'),
            'day': date.strftime('%a'),
            'drops': daily_drops,
        })
    
    # Relatórios recentes
    recent_reports = user_reports[:5]
    
    # Performance (comparação com semana anterior)
    this_week_cars = user_reports.filter(
        created_at__date__gte=this_week_start
    ).aggregate(total=Sum('total_cleaned'))['total'] or 0
    
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)
    last_week_cars = user_reports.filter(
        created_at__date__gte=last_week_start,
        created_at__date__lte=last_week_end
    ).aggregate(total=Sum('total_cleaned'))['total'] or 0
    
    if last_week_cars > 0:
        performance = round(((this_week_cars - last_week_cars) / last_week_cars) * 100, 1)
    else:
        performance = 100 if this_week_cars > 0 else 0
    
    context = {
        'stats': stats,
        'totals': totals,
        'daily_data': daily_data,
        'drops_data': drops_data,
        'recent_reports': recent_reports,
        'performance': performance,
        'this_week_cars': this_week_cars,
        'last_week_cars': last_week_cars,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def admin_dashboard_view(request):
    """Dashboard administrativo consolidado"""
    now = timezone.now()
    today = now.date()
    this_month_start = today.replace(day=1)
    
    # Estatísticas gerais
    all_reports = Report.objects.all()
    all_users = User.objects.filter(is_active=True, is_superuser=False)
    
    general_stats = {
        'total_users': all_users.count(),
        'total_reports': all_reports.count(),
        'reports_this_month': all_reports.filter(created_at__date__gte=this_month_start).count(),
        'active_users_today': all_reports.filter(created_at__date=today).values('user').distinct().count(),
    }
    
    # Totais consolidados
    consolidated_totals = all_reports.aggregate(
        total_cars_cleaned=Sum('total_cleaned'),
        total_forecasted_drops=Sum('forecasted_drops'),
        avg_cars_per_report=Avg('total_cleaned'),
    )
    
    # Dados por usuário
    user_stats = []
    for user in all_users:
        user_reports = all_reports.filter(user=user)
        user_stats.append({
            'user': user,
            'total_reports': user_reports.count(),
            'total_cars': user_reports.aggregate(total=Sum('total_cleaned'))['total'] or 0,
            'reports_sent': user_reports.filter(email_status='sent').count(),
            'last_report': user_reports.first(),
        })
    
    # Ordenar por total de carros
    user_stats.sort(key=lambda x: x['total_cars'], reverse=True)
    
    # Dados dos últimos 7 dias consolidados
    daily_consolidated = []
    for i in range(7):
        date = today - timedelta(days=6-i)
        day_reports = all_reports.filter(created_at__date=date)
        
        daily_cars = day_reports.aggregate(total=Sum('total_cleaned'))['total'] or 0
        daily_drops = day_reports.aggregate(total=Sum('forecasted_drops'))['total'] or 0
        daily_users = day_reports.values('user').distinct().count()
        
        daily_consolidated.append({
            'date': date.strftime('%d/%m'),
            'day': date.strftime('%a'),
            'cars': daily_cars,
            'drops': daily_drops,
            'users': daily_users,
        })
    
    # Status dos e-mails
    email_stats = all_reports.values('email_status').annotate(
        count=Count('id')
    ).order_by('email_status')
    
    context = {
        'general_stats': general_stats,
        'consolidated_totals': consolidated_totals,
        'user_stats': user_stats,
        'daily_consolidated': daily_consolidated,
        'email_stats': email_stats,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)