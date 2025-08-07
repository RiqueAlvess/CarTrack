from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import EmailRecipient


@login_required
def email_list_view(request):
    """Lista e gerencia destinatários de e-mail do usuário"""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        
        if not email:
            messages.error(request, 'E-mail é obrigatório')
            return redirect('emails:list')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'E-mail inválido')
            return redirect('emails:list')
        
        # Verificar se já existe
        if EmailRecipient.objects.filter(user=request.user, email=email).exists():
            messages.warning(request, 'Este e-mail já está cadastrado')
            return redirect('emails:list')
        
        # Criar destinatário
        EmailRecipient.objects.create(
            user=request.user,
            email=email,
            name=name or email.split('@')[0]
        )
        
        messages.success(request, f'E-mail {email} adicionado com sucesso!')
        return redirect('emails:list')
    
    # Listar destinatários
    recipients = EmailRecipient.objects.filter(user=request.user, is_active=True)
    
    context = {
        'recipients': recipients,
        'recipients_count': recipients.count(),
    }
    
    return render(request, 'emails/list.html', context)


@login_required
def add_email_view(request):
    """Adiciona um novo destinatário de e-mail"""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        
        if not email:
            messages.error(request, 'E-mail é obrigatório')
            return render(request, 'emails/add.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'E-mail inválido')
            return render(request, 'emails/add.html')
        
        # Verificar se já existe
        if EmailRecipient.objects.filter(user=request.user, email=email).exists():
            messages.warning(request, 'Este e-mail já está cadastrado')
            return render(request, 'emails/add.html')
        
        # Criar destinatário
        EmailRecipient.objects.create(
            user=request.user,
            email=email,
            name=name or email.split('@')[0]
        )
        
        messages.success(request, f'E-mail {email} adicionado com sucesso!')
        return redirect('emails:list')
    
    return render(request, 'emails/add.html')


@login_required
def delete_email_view(request, pk):
    """Remove um destinatário de e-mail"""
    recipient = get_object_or_404(EmailRecipient, pk=pk, user=request.user)
    
    if request.method == 'POST':
        email = recipient.email
        recipient.delete()
        messages.success(request, f'E-mail {email} removido com sucesso!')
        return redirect('emails:list')
    
    context = {
        'recipient': recipient,
    }
    
    return render(request, 'emails/delete.html', context)


@login_required
@require_POST
def toggle_email_status(request, pk):
    """Ativa/desativa um destinatário de e-mail"""
    recipient = get_object_or_404(EmailRecipient, pk=pk, user=request.user)
    
    recipient.is_active = not recipient.is_active
    recipient.save()
    
    status = 'ativado' if recipient.is_active else 'desativado'
    
    return JsonResponse({
        'success': True,
        'message': f'E-mail {status} com sucesso!',
        'is_active': recipient.is_active
    })