from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('core:home')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')
    
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        
        # Atualizar configurações SMTP - Agora com Outlook como padrão
        user.smtp_email = request.POST.get('smtp_email', '')
        user.smtp_password = request.POST.get('smtp_password', '')
        user.smtp_host = request.POST.get('smtp_host', 'smtp-mail.outlook.com')  # Outlook padrão
        user.smtp_port = int(request.POST.get('smtp_port', 587))
        user.smtp_use_tls = request.POST.get('smtp_use_tls') == 'on'
        
        user.save()
        messages.success(request, 'Configurações salvas com sucesso!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')

@login_required
@require_POST
def test_email_view(request):
    user = request.user
    
    if not user.smtp_email or not user.smtp_password:
        return JsonResponse({
            'success': False, 
            'message': 'Configure primeiro o e-mail SMTP'
        })
    
    try:
        # Testar conexão SMTP
        server = smtplib.SMTP(user.smtp_host, user.smtp_port)
        if user.smtp_use_tls:
            server.starttls()
        server.login(user.smtp_email, user.smtp_password)
        
        # Enviar e-mail de teste para o endereço específico do Henrique
        test_email = 'henrique.alves.siqueira@hotmail.com'
        
        msg = MIMEMultipart()
        msg['From'] = user.smtp_email
        msg['To'] = test_email
        msg['Subject'] = 'Teste de Configuração SMTP - CarTrack'
        
        body = f"""
        Olá Henrique,
        
        Este é um e-mail de teste do sistema CarTrack.
        
        Usuário que realizou o teste: {user.get_full_name() or user.username}
        E-mail do usuário: {user.email}
        Data/Hora do teste: {request.META.get('HTTP_DATE', 'Não informado')}
        
        Se você recebeu este e-mail, as configurações SMTP estão funcionando corretamente!
        
        Detalhes da configuração:
        - Servidor SMTP: {user.smtp_host}
        - Porta: {user.smtp_port}
        - TLS: {'Ativado' if user.smtp_use_tls else 'Desativado'}
        
        Atenciosamente,
        Sistema CarTrack
        """
        
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        
        return JsonResponse({
            'success': True, 
            'message': f'E-mail de teste enviado com sucesso para {test_email}!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao enviar e-mail: {str(e)}'
        })