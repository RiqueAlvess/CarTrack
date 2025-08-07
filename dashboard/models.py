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
    
    TIPO_SERVICO_CHOICES = [
        ('limpeza_simples', 'Limpeza Simples'),
        ('limpeza_completa', 'Limpeza Completa'),
        ('enceramento', 'Enceramento'),
        ('lavagem_motor', 'Lavagem do Motor'),
        ('aspiracao', 'Aspiração'),
        ('outros', 'Outros'),
    ]
    
    CONDICAO_VEICULO_CHOICES = [
        ('limpo', 'Limpo'),
        ('sujo', 'Sujo'),
        ('muito_sujo', 'Muito Sujo'),
        ('necessita_manutencao', 'Necessita Manutenção'),
    ]
    
    # Relacionamentos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relatorios')
    # Usar string para evitar import circular
    empresa = models.ForeignKey('dashboard.Empresa', on_delete=models.CASCADE, related_name='relatorios')
    
    # Dados básicos do relatório
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_servico = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho')
    
    # Dados do veículo
    placa_veiculo = models.CharField(max_length=10, help_text='Ex: ABC-1234')
    modelo_veiculo = models.CharField(max_length=100, blank=True)
    cor_veiculo = models.CharField(max_length=50, blank=True)
    quilometragem = models.PositiveIntegerField(blank=True, null=True)
    
    # Detalhes do serviço
    tipo_servico = models.CharField(max_length=30, choices=TIPO_SERVICO_CHOICES)
    condicao_inicial = models.CharField(max_length=30, choices=CONDICAO_VEICULO_CHOICES)
    condicao_final = models.CharField(max_length=30, choices=CONDICAO_VEICULO_CHOICES)
    
    # Tempo de serviço
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField(blank=True, null=True)
    
    # Observações e detalhes
    observacoes = models.TextField(blank=True, help_text='Observações gerais sobre o serviço')
    problemas_encontrados = models.TextField(blank=True, help_text='Problemas ou danos identificados')
    produtos_utilizados = models.TextField(blank=True, help_text='Lista de produtos utilizados')
    
    # Localização
    local_servico = models.CharField(max_length=200, blank=True, help_text='Local onde foi realizado o serviço')
    
    # Fotos (campos para URLs das imagens)
    foto_antes = models.URLField(blank=True, help_text='Foto do veículo antes do serviço')
    foto_depois = models.URLField(blank=True, help_text='Foto do veículo após o serviço')
    foto_adicional = models.URLField(blank=True, help_text='Foto adicional se necessário')
    
    # Controle de qualidade
    avaliacao_qualidade = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        blank=True, 
        null=True,
        help_text='Avaliação de 1 a 5'
    )
    
    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-data_criacao']
        
    def __str__(self):
        return f"Relatório {self.placa_veiculo} - {self.data_servico} ({self.get_status_display()})"
    
    @property
    def duracao_servico(self):
        """Calcula a duração do serviço em minutos"""
        if self.hora_fim and self.hora_inicio:
            inicio = self.hora_inicio
            fim = self.hora_fim
            # Convertendo para minutos desde meia-noite
            inicio_min = inicio.hour * 60 + inicio.minute
            fim_min = fim.hour * 60 + fim.minute
            return fim_min - inicio_min
        return None
    
    @property
    def duracao_formatada(self):
        """Retorna a duração formatada como string"""
        duracao = self.duracao_servico
        if duracao:
            horas = duracao // 60
            minutos = duracao % 60
            if horas > 0:
                return f"{horas}h {minutos}min"
            else:
                return f"{minutos}min"
        return "N/A"
    
    def save(self, *args, **kwargs):
        # Se não foi definida empresa, usa a empresa ativa do usuário
        if not self.empresa_id and self.usuario:
            try:
                # Import aqui para evitar circular imports
                from django.apps import apps
                EmpresaAtivaUsuario = apps.get_model('dashboard', 'EmpresaAtivaUsuario')
                empresa_ativa = EmpresaAtivaUsuario.objects.get(usuario=self.usuario)
                self.empresa = empresa_ativa.empresa
            except Exception:
                pass
        
        super().save(*args, **kwargs)