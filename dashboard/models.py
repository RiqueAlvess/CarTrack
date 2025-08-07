from django.db import models
from django.conf import settings

class Empresa(models.Model):
    nome = models.CharField(max_length=200)
    cidade = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    usuarios = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UsuarioEmpresa')
    
    def __str__(self):
        return self.nome

class UsuarioEmpresa(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_vinculo = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'empresa')
        

class EmpresaAtivaUsuario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Empresa ativa do usuário"
        verbose_name_plural = "Empresas ativas dos usuários"

    def __str__(self):
        return f"{self.usuario.username} → {self.empresa.nome if self.empresa else 'Nenhuma'}"


class Relatorio(models.Model):
    """
    Modelo de Relatório para dashboard - pode ser usado para relatórios internos
    """
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='relatorios_dashboard'
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Dados específicos do dashboard
    total_funcionarios = models.IntegerField(default=0)
    funcionarios_ativos = models.IntegerField(default=0)
    funcionarios_ferias = models.IntegerField(default=0)
    funcionarios_afastados = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Relatório Dashboard"
        verbose_name_plural = "Relatórios Dashboard"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo} - {self.empresa.nome}"