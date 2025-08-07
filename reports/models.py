from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()

class Report(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Enviado'),
        ('not_sent', 'Não Enviado'),
        ('error', 'Erro no Envio'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Usuário'
    )
    
    # Campos do relatório (apenas numéricos)
    ready_line = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Ready Line'
    )
    vip_line = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='VIP Line'
    )
    overflow_kiosk = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Overflow Kiosk'
    )
    overflow_2 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Overflow 2'
    )
    black_top = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Black Top'
    )
    return_line = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Return Line'
    )
    mecanico = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Mecânico'
    )
    gas_run = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Gas Run'
    )
    total_cleaned = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Total Cleaned'
    )
    forecasted_drops = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Forecasted Drops'
    )
    
    # Controle de envio
    send_email = models.BooleanField(default=False, verbose_name='Enviar por E-mail')
    email_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='not_sent',
        verbose_name='Status do E-mail'
    )
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Enviado em')
    error_message = models.TextField(blank=True, null=True, verbose_name='Mensagem de Erro')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Relatório {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def total_cars_cleaned(self):
        """Calcula o total de carros limpos"""
        return (self.ready_line + self.vip_line + self.overflow_kiosk + 
                self.overflow_2 + self.black_top + self.return_line + 
                self.mecanico + self.gas_run)
    
    def can_resend(self):
        """Verifica se o relatório pode ser reenviado"""
        return self.email_status in ['not_sent', 'error']