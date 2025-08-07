from django.contrib import admin
from .models import Relatorio

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = (
        'data_servico', 
        'usuario', 
        'empresa',
        'total_count_cleaned_cars',
        'forecasted_drops',
        'status', 
        'data_criacao'
    )
    
    list_filter = (
        'status', 
        'data_servico',
        'empresa',
        'data_criacao'
    )
    
    search_fields = (
        'usuario__username',
        'usuario__email',
        'empresa__RAZAOSOCIAL'
    )
    
    date_hierarchy = 'data_servico'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'empresa', 'data_servico', 'status')
        }),
        ('Contagem de Carros por Área', {
            'fields': (
                'ready_line', 
                'vip_line', 
                'overflow_kiosk', 
                'overflow_2', 
                'black_top', 
                'return_line', 
                'mecanico', 
                'gas_run'
            )
        }),
        ('Totais', {
            'fields': ('total_count_cleaned_cars', 'forecasted_drops'),
            'description': 'Total de carros limpos é calculado automaticamente'
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Datas do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('total_count_cleaned_cars', 'data_criacao', 'data_atualizacao')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario', 'empresa')
    
    # Ações em massa
    actions = ['marcar_como_concluido', 'marcar_como_enviado']
    
    def marcar_como_concluido(self, request, queryset):
        updated = queryset.update(status='concluido')
        self.message_user(request, f'{updated} relatório(s) marcado(s) como concluído(s).')
    marcar_como_concluido.short_description = "Marcar como concluído"
    
    def marcar_como_enviado(self, request, queryset):
        updated = queryset.update(status='enviado')
        self.message_user(request, f'{updated} relatório(s) marcado(s) como enviado(s).')
    marcar_como_enviado.short_description = "Marcar como enviado"