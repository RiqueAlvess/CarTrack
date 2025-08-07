from django.contrib import admin
from .models import Relatorio


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ['id', 'empresa', 'usuario', 'total_cleaned', 'forecasted_drops', 'enviado_por_email', 'data_criacao']
    list_filter = ['enviado_por_email', 'data_criacao', 'empresa']
    search_fields = ['empresa__nome', 'usuario__username']
    date_hierarchy = 'data_criacao'
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('empresa', 'usuario', 'enviado_por_email', 'data_envio')
        }),
        ('Dados do Relatório', {
            'fields': (
                ('ready_line', 'vip_line'),
                ('overflow_kiosk', 'overflow_2'),
                ('black_top', 'return_line'),
                ('mecanico', 'gas_run'),
                ('total_cleaned', 'forecasted_drops'),
            )
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )