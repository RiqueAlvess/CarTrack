from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Relatorio(models.Model):
    # Relacionamento com usuário
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='relatorios',
        verbose_name='Usuário'
    )
    
    # Campo de texto simples para unidade/empresa
    unidade_empresa = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Unidade/Empresa',
        help_text='Nome da unidade ou empresa'
    )
    
    # Campos do relatório
    ready_line = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Ready Line'
    )
    
    vip_line = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='VIP Line'
    )
    
    overflow_kiosk = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Overflow Kiosk'
    )
    
    overflow_2 = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Overflow 2'
    )
    
    black_top = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Black Top'
    )
    
    return_line = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Return Line'
    )
    
    mecanico = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Mecânico'
    )
    
    gas_run = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Gas Run'
    )
    
    total_cleaned = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Total de Carros Limpos'
    )
    
    forecasted_drops = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Previsão de Drops'
    )
    
    # Configurações de envio
    enviar_por_email = models.BooleanField(
        default=False,
        verbose_name='Enviar por e-mail'
    )
    
    # Status do envio
    email_enviado = models.BooleanField(
        default=False,
        verbose_name='E-mail enviado'
    )
    
    tentativas_envio = models.PositiveIntegerField(
        default=0,
        verbose_name='Tentativas de envio'
    )
    
    erro_envio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Erro no envio'
    )
    
    # Timestamps
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de criação'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de atualização'
    )
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-data_criacao']
        
    def __str__(self):
        return f"Relatório de {self.usuario.get_full_name() or self.usuario.username} - {self.data_criacao.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def total_carros(self):
        """Calcula o total de carros processados"""
        return (
            self.ready_line + self.vip_line + self.overflow_kiosk + 
            self.overflow_2 + self.black_top + self.return_line + 
            self.mecanico + self.gas_run
        )
    
    @property
    def data_formatada(self):
        """Retorna a data formatada"""
        return self.data_criacao.strftime('%d/%m/%Y')
    
    @property
    def hora_formatada(self):
        """Retorna a hora formatada"""
        return self.data_criacao.strftime('%H:%M')


class ImagemRelatorio(models.Model):
    """Modelo para armazenar imagens dos relatórios"""
    relatorio = models.ForeignKey(
        Relatorio,
        on_delete=models.CASCADE,
        related_name='imagens',
        verbose_name='Relatório'
    )
    
    imagem = models.ImageField(
        upload_to='relatorios/%Y/%m/%d/',
        verbose_name='Imagem'
    )
    
    descricao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Descrição'
    )
    
    data_upload = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data do upload'
    )
    
    class Meta:
        verbose_name = 'Imagem do Relatório'
        verbose_name_plural = 'Imagens dos Relatórios'
        ordering = ['data_upload']
        
    def __str__(self):
        return f"Imagem do {self.relatorio} - {self.data_upload.strftime('%d/%m/%Y %H:%M')}"