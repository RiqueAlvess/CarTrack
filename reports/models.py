from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Relatorio(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('concluido', 'Concluído'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Relacionamentos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relatorios_cartrack')
    empresa = models.ForeignKey('dashboard.Empresa', on_delete=models.CASCADE, related_name='relatorios_cartrack')
    
    # Dados básicos do relatório
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_servico = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='concluido')
    
    # Campos de contagem de carros - TODOS NUMÉRICOS
    ready_line = models.PositiveIntegerField(default=0, help_text='Ready line')
    vip_line = models.PositiveIntegerField(default=0, help_text='VIP line')
    overflow_kiosk = models.PositiveIntegerField(default=0, help_text='Overflow Kiosk')
    overflow_2 = models.PositiveIntegerField(default=0, help_text='Overflow 2')
    black_top = models.PositiveIntegerField(default=0, help_text='Black top')
    return_line = models.PositiveIntegerField(default=0, help_text='Return')
    mecanico = models.PositiveIntegerField(default=0, help_text='Mecânico')
    gas_run = models.PositiveIntegerField(default=0, help_text='Gas run')
    
    # Total calculado automaticamente
    total_count_cleaned_cars = models.PositiveIntegerField(default=0, help_text='Total count of cleaned cars')
    
    # Previsão
    forecasted_drops = models.PositiveIntegerField(default=0, help_text='Forecasted drops')
    
    # Observações opcionais
    observacoes = models.TextField(blank=True, help_text='Observações adicionais')
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-data_criacao']
        
    def __str__(self):
        return f"Relatório {self.data_servico} - Total: {self.total_count_cleaned_cars} carros"
    
    def save(self, *args, **kwargs):
        # Calcular total automaticamente
        self.total_count_cleaned_cars = (
            self.ready_line + 
            self.vip_line + 
            self.overflow_kiosk + 
            self.overflow_2 + 
            self.black_top + 
            self.return_line + 
            self.mecanico + 
            self.gas_run
        )
        
        # Se não foi definida empresa, usa a empresa ativa do usuário
        if not self.empresa_id and self.usuario:
            try:
                from django.apps import apps
                EmpresaAtivaUsuario = apps.get_model('dashboard', 'EmpresaAtivaUsuario')
                empresa_ativa = EmpresaAtivaUsuario.objects.get(usuario=self.usuario)
                self.empresa = empresa_ativa.empresa
            except Exception:
                pass
        
        super().save(*args, **kwargs)