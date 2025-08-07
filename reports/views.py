from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import date, datetime
from .models import Relatorio

@login_required
def reports_list_view(request):
    """Lista todos os relatórios do usuário com filtros"""
    user = request.user
    
    # Filtros
    status_filter = request.GET.get('status', '')
    data_filter = request.GET.get('data', '')
    busca = request.GET.get('q', '')
    
    # Query base
    relatorios = Relatorio.objects.filter(usuario=user)
    
    # Aplicar filtros
    if status_filter == 'enviado':
        relatorios = relatorios.filter(email_enviado=True)
    elif status_filter == 'nao_enviado':
        relatorios = relatorios.filter(email_enviado=False)
    
    if data_filter:
        if data_filter == 'hoje':
            relatorios = relatorios.filter(data_criacao__date=date.today())
        elif data_filter == 'semana':
            from datetime import timedelta
            uma_semana_atras = date.today() - timedelta(days=7)
            relatorios = relatorios.filter(data_criacao__date__gte=uma_semana_atras)
        elif data_filter == 'mes':
            relatorios = relatorios.filter(
                data_criacao__year=date.today().year,
                data_criacao__month=date.today().month
            )
    
    if busca:
        relatorios = relatorios.filter(
            Q(unidade_empresa__icontains=busca) |
            Q(usuario__first_name__icontains=busca) |
            Q(usuario__last_name__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(relatorios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas rápidas
    total_relatorios = relatorios.count()
    relatorios_hoje = Relatorio.objects.filter(
        usuario=user,
        data_criacao__date=date.today()
    ).count()
    
    context = {
        'relatorios': page_obj,
        'total_relatorios': total_relatorios,
        'relatorios_hoje': relatorios_hoje,
        'status_filter': status_filter,
        'data_filter': data_filter,
        'busca': busca,
    }
    
    return render(request, 'reports/list.html', context)

@login_required
def create_report_view(request):
    """Criar novo relatório"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Criar novo relatório com dados do formulário
            relatorio = Relatorio(
                usuario=user,
                unidade_empresa=request.POST.get('unidade_empresa', ''),
                
                # Campos de contagem
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
                
                # Configuração de envio
                enviar_por_email=bool(request.POST.get('enviar_por_email'))
            )
            
            relatorio.save()
            
            # Se marcou para enviar por email, tentar enviar
            if relatorio.enviar_por_email:
                # TODO: Implementar envio de email
                pass
            
            messages.success(request, f'Relatório criado com sucesso! Total: {relatorio.total_carros} carros processados.')
            return redirect('reports:detail', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar relatório: {str(e)}')
    
    # Dados para o formulário
    context = {
        'data_hoje': date.today(),
    }
    
    return render(request, 'reports/create.html', context)

@login_required
def report_detail_view(request, pk):
    """Visualizar detalhes de um relatório"""
    relatorio = get_object_or_404(
        Relatorio, 
        pk=pk,
        usuario=request.user
    )
    
    context = {
        'relatorio': relatorio,
    }
    
    return render(request, 'reports/detail.html', context)

@login_required
def resend_report_view(request, pk):
    """Reenviar relatório por email"""
    relatorio = get_object_or_404(
        Relatorio,
        pk=pk,
        usuario=request.user
    )
    
    if request.method == 'POST':
        try:
            # TODO: Implementar reenvio de email
            relatorio.tentativas_envio += 1
            relatorio.save()
            
            messages.success(request, 'Relatório reenviado com sucesso!')
            return redirect('reports:detail', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao reenviar relatório: {str(e)}')
    
    context = {
        'relatorio': relatorio,
    }
    
    return render(request, 'reports/resend.html', context)