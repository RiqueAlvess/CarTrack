from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='E-mail usado para login no sistema'
    )
    
    # Configurações SMTP do usuário - Configuração padrão para Outlook/Hotmail
    smtp_email = models.EmailField(
        blank=True,
        null=True,
        help_text='E-mail SMTP para envio de relatórios'
    )
    smtp_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Senha do e-mail SMTP (use senha de app para Outlook/Hotmail)'
    )
    smtp_host = models.CharField(
        max_length=255,
        default='smtp-mail.outlook.com',  # Mudança para Outlook
        help_text='Servidor SMTP'
    )
    smtp_port = models.IntegerField(
        default=587,  # Porta padrão para Outlook
        help_text='Porta SMTP'
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text='Usar TLS para conexão SMTP'
    )
    
    # Configurações adicionais
    is_email_configured = models.BooleanField(
        default=False,
        help_text='Indica se o usuário configurou o SMTP'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"
    
    def save(self, *args, **kwargs):
        # Verifica se o SMTP está configurado
        if self.smtp_email and self.smtp_password:
            self.is_email_configured = True
        else:
            self.is_email_configured = False
        super().save(*args, **kwargs)