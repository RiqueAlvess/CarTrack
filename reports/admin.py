from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'created_at', 
        'total_cars_cleaned',
        'total_cleaned', 
        'forecasted_drops',
        'email_status',
        'send_email'
    )
    
    list_filter = (
        'email_status',
        'send_email',
        'created_at',
        'user'
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'email_sent_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'created_at', 'updated_at')
        }),
        ('Dados do Relatório', {
            'fields': (
                'ready_line', 'vip_line', 'overflow_kiosk', 'overflow_2',
                'black_top', 'return_line', 'mecanico', 'gas_run',
                'total_cleaned', 'forecasted_drops'
            )
        }),
        ('Controle de E-mail', {
            'fields': (
                'send_email', 'email_status', 'email_sent_at', 'error_message'
            )
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['-created_at']