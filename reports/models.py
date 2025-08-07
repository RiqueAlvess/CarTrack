from django.db import models
from django.conf import settings
from dashboard.models import Empresa


class Relatorio(models.Model):
    # Referência à empresa
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='relatorios_reports'
    )
    
    # Informações básicas do relatório
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Campos do relatório (baseado nas imagens)
    ready_line = models.CharField(max_length=10, blank=True, null=True)
    vip_line = models.CharField(max_length=10, blank=True, null=True)
    overflow_kiosk = models.CharField(max_length=10, blank=True, null=True)
    overflow_2 = models.CharField(max_length=10, blank=True, null=True)
    black_top = models.CharField(max_length=10, blank=True, null=True)
    return_line = models.CharField(max_length=10, blank=True, null=True)
    mecanico = models.CharField(max_length=10, blank=True, null=True)
    gas_run = models.CharField(max_length=10, blank=True, null=True)
    
    # Totais
    total_cleaned = models.IntegerField(default=0)
    forecasted_drops = models.IntegerField(default=0)
    
    # Status de envio
    enviado_por_email = models.BooleanField(default=False)
    data_envio = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Relatório {self.id} - {self.empresa.nome} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"