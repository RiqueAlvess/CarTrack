from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

User = get_user_model()

class EmailRecipient(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='email_recipients',
        verbose_name='Usuário'
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name='E-mail'
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nome'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Destinatário de E-mail'
        verbose_name_plural = 'Destinatários de E-mail'
        unique_together = ['user', 'email']
        ordering = ['email']
    
    def __str__(self):
        return f"{self.name or self.email} ({self.user.username})"