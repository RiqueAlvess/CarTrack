from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timedelta

from .models import Report
from emails.models import EmailRecipient


def send_report_email(report):
    """Envia o relatório por e-mail"""
    user = report.user
    
    if not user.smtp_email or not user.smtp_password:
        return {'success': False, 'message': 'Configurações SMTP não encontradas'}
    
    recipients = EmailRecipient.objects.filter(user=user, is_active=True)
    if not recipients.exists():
        return {'success': False, 'message': 'Nenhum destinatário configurado'}
    
    try:
        # Configurar SMTP
        server = smtplib.SMTP(user.smtp_host, user.smtp_port)
        if user.smtp_use_tls:
            server.starttls()
        server.login(user.smtp_email, user.smtp_password)
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = user.smtp_email
        msg['To'] = ', '.join([r.email for r in recipients])
        msg['Subject'] = f'Relatório CarTrack - {report.created_at.strftime("%d/%m/%Y %H:%M")}'
        
        # Corpo do e-mail
        body = f"""
Relatório de Carros - {report.created_at.strftime("%d/%m/%Y %H:%M")}
Usuário: {user.get_full_name() or user.username}

DADOS DO RELATÓRIO:
==================
Ready Line: {report.ready_line}
VIP Line: {report.vip_line}
Overflow Kiosk: {report.overflow_kiosk}
Overflow 2: {report.overflow_2}
Black Top: {report.black_top}
Return Line: {report.return_line}
Mecânico: {report.mecanico}
Gas Run: {report.gas_run}
Total Cleaned: {report.total_cleaned}
Forecasted Drops: {report.forecasted_drops}

TOTAL DE CARROS LIMPOS: {report.total_cars_cleaned}

--
Sistema CarTrack
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar e-mail
        server.send_message(msg)
        server.quit()
        
        return {'success': True, 'message': 'E-mail enviado com sucesso'}
        
    except Exception as e:
        return {'success': False, 'message': f'Erro ao enviar e-mail: {str(e)}'}


@login_required
def reports_list_view(request):
    """Lista os relatórios do usuário"""
    reports = Report.objects.filter(user=request.user)
    
    # Filtros
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        reports = reports.filter(
            Q(created_at__date__icontains=search) |
            Q(total_cleaned__icontains=search)
        )
    
    if status_filter:
        reports = reports.filter(email_status=status_filter)
    
    # Paginação
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'search': search,
        'status_filter': status_filter,
    }
    
    return render(request, 'reports/list.html', context)


@login_required
def create_report_view(request):
    """Cria um novo relatório"""
    if request.method == 'POST':
        try:
            # Criar o relatório
            report = Report.objects.create(
                user=request.user,
                ready_line=int(request.POST.get('ready_line', 0)),
                vip_line=int(request.POST.get('vip_line', 0)),
                overflow_kiosk=int(request.POST.get('overflow_kiosk', 0)),
                overflow_2=int(request.POST.get('overflow_2', 0)),
                black_top=int(request.POST.get('black_top', 0)),
                return_line=int(request.POST.get('return_line', 0)),
                mecanico=int(request.POST.get('mecanico', 0)),
                gas_run=int(request.POST.get('gas_run', 0)),
                total_cleaned=int(request.POST.get('total_cleaned', 0)),
                forecasted_drops=int(request.POST.get('forecasted_drops', 0)),
                send_email=request.POST.get('send_email') == 'on'
            )
            
            # Enviar e-mail se solicitado
            if report.send_email:
                result = send_report_email(report)
                if result['success']:
                    report.email_status = 'sent'
                    report.email_sent_at = timezone.now()
                    report.save()
                    messages.success(request, 'Relatório criado e enviado por e-mail com sucesso!')
                else:
                    report.email_status = 'error'
                    report.error_message = result['message']
                    report.save()
                    messages.warning(request, f'Relatório criado, mas erro no envio: {result["message"]}')
            else:
                messages.success(request, 'Relatório criado com sucesso!')
            
            return redirect('reports:list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar relatório: {str(e)}')
    
    return render(request, 'reports/create.html')


@login_required
def report_detail_view(request, pk):
    """Exibe detalhes do relatório"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    context = {
        'report': report,
    }
    
    return render(request, 'reports/detail.html', context)


@login_required
@require_POST
def resend_report_view(request, pk):
    """Reenvia um relatório por e-mail"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    if not report.can_resend():
        return JsonResponse({
            'success': False, 
            'message': 'Este relatório não pode ser reenviado'
        })
    
    result = send_report_email(report)
    
    if result['success']:
        report.email_status = 'sent'
        report.email_sent_at = timezone.now()
        report.error_message = None
        report.save()
        return JsonResponse({
            'success': True, 
            'message': 'Relatório reenviado com sucesso!'
        })
    else:
        report.email_status = 'error'
        report.error_message = result['message']
        report.save()
        return JsonResponse({
            'success': False, 
            'message': result['message']
        })


@login_required
def copy_report_view(request, pk):
    """Copia conteúdo do relatório para área de transferência"""
    report = get_object_or_404(Report, pk=pk, user=request.user)
    
    content = f"""Relatório CarTrack - {report.created_at.strftime("%d/%m/%Y %H:%M")}
Usuário: {request.user.get_full_name() or request.user.username}

Ready Line: {report.ready_line}
VIP Line: {report.vip_line}
Overflow Kiosk: {report.overflow_kiosk}
Overflow 2: {report.overflow_2}
Black Top: {report.black_top}
Return Line: {report.return_line}
Mecânico: {report.mecanico}
Gas Run: {report.gas_run}
Total Cleaned: {report.total_cleaned}
Forecasted Drops: {report.forecasted_drops}

Total de Carros Limpos: {report.total_cars_cleaned}"""
    
    return HttpResponse(content, content_type='text/plain')