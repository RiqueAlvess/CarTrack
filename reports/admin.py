from django.contrib import admin
from .models import Relatorio

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = (
        'placa_veiculo', 
        'data_servico', 
        'tipo_servico', 
        'status', 
        'usuario', 
        'empresa',
        'duracao_formatada',
        'data_criacao'
    )
    
    list_filter = (
        'status', 
        'tipo_servico', 
        'condicao_inicial',
        'condicao_final',
        'data_servico',
        'empresa',
        'data_criacao'
    )
    
    search_fields = (
        'placa_veiculo', 
        'modelo_veiculo', 
        'cor_veiculo',
        'usuario__username',
        'usuario__email',
        'local_servico'
    )
    
    date_hierarchy = 'data_servico'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'empresa', 'data_servico', 'status')
        }),
        ('Dados do Veículo', {
            'fields': ('placa_veiculo', 'modelo_veiculo', 'cor_veiculo', 'quilometragem')
        }),
        ('Detalhes do Serviço', {
            'fields': ('tipo_servico', 'hora_inicio', 'hora_fim', 'local_servico')
        }),
        ('Condições', {
            'fields': ('condicao_inicial', 'condicao_final', 'avaliacao_qualidade')
        }),
        ('Observações', {
            'fields': ('observacoes', 'problemas_encontrados', 'produtos_utilizados'),
            'classes': ('collapse',)
        }),
        ('Fotos', {
            'fields': ('foto_antes', 'foto_depois', 'foto_adicional'),
            'classes': ('collapse',)
        }),
        ('Datas do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    # Filtros personalizados
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario', 'empresa')
    
    # Ações em massa
    actions = ['marcar_como_concluido', 'marcar_como_enviado', 'marcar_como_cancelado']
    
    def marcar_como_concluido(self, request, queryset):
        updated = queryset.update(status='concluido')
        self.message_user(request, f'{updated} relatório(s) marcado(s) como concluído(s).')
    marcar_como_concluido.short_description = "Marcar como concluído"
    
    def marcar_como_enviado(self, request, queryset):
        updated = queryset.update(status='enviado')
        self.message_user(request, f'{updated} relatório(s) marcado(s) como enviado(s).')
    marcar_como_enviado.short_description = "Marcar como enviado"
    
    def marcar_como_cancelado(self, request, queryset):
        updated = queryset.update(status='cancelado')
        self.message_user(request, f'{updated} relatório(s) marcado(s) como cancelado(s).')
    marcar_como_cancelado.short_description = "Marcar como cancelado"