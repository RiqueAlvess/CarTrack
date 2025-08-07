from django.contrib import admin
from .models import Relatorio, ImagemRelatorio

class ImagemRelatorioInline(admin.TabularInline):
    model = ImagemRelatorio
    extra = 1
    readonly_fields = ('data_upload',)

@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'data_formatada',
        'hora_formatada',
        'total_carros',
        'total_cleaned',
        'forecasted_drops',
        'email_enviado',
        'enviar_por_email'
    )
    
    list_filter = (
        'email_enviado',
        'enviar_por_email',
        'data_criacao',
        'usuario'
    )
    
    search_fields = (
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name'
    )
    
    readonly_fields = (
        'data_criacao',
        'data_atualizacao',
        'total_carros'
    )
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'usuario',
                'data_criacao',
                'data_atualizacao'
            )
        }),
        ('Dados do Relatório', {
            'fields': (
                'ready_line',
                'vip_line',
                'overflow_kiosk',
                'overflow_2',
                'black_top',
                'return_line',
                'mecanico',
                'gas_run',
                'total_cleaned',
                'forecasted_drops'
            )
        }),
        ('Configurações de E-mail', {
            'fields': (
                'enviar_por_email',
                'email_enviado',
                'tentativas_envio',
                'erro_envio'
            )
        }),
    )
    
    inlines = [ImagemRelatorioInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)

@admin.register(ImagemRelatorio)
class ImagemRelatorioAdmin(admin.ModelAdmin):
    list_display = (
        'relatorio',
        'descricao',
        'data_upload'
    )
    
    list_filter = (
        'data_upload',
        'relatorio__usuario'
    )
    
    readonly_fields = ('data_upload',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(relatorio__usuario=request.user)