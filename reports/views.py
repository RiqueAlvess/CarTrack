from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.apps import apps
from datetime import date, datetime
from .models import Relatorio

@login_required
def relatorios_list(request):
    """Lista todos os relatórios do usuário com filtros"""
    user = request.user
    
    # Obter empresa ativa do usuário
    try:
        EmpresaAtivaUsuario = apps.get_model('dashboard', 'EmpresaAtivaUsuario')
        empresa_ativa = EmpresaAtivaUsuario.objects.get(usuario=user)
        empresa = empresa_ativa.empresa
    except Exception:
        messages.error(request, 'Nenhuma empresa ativa selecionada.')
        return redirect('core:home')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    data_filter = request.GET.get('data', '')
    busca = request.GET.get('q', '')
    
    # Query base
    relatorios = Relatorio.objects.filter(
        usuario=user,
        empresa=empresa
    ).select_related('empresa')
    
    # Aplicar filtros
    if status_filter:
        relatorios = relatorios.filter(status=status_filter)
    
    if data_filter:
        if data_filter == 'hoje':
            relatorios = relatorios.filter(data_servico=date.today())
        elif data_filter == 'semana':
            from datetime import timedelta
            uma_semana_atras = date.today() - timedelta(days=7)
            relatorios = relatorios.filter(data_servico__gte=uma_semana_atras)
        elif data_filter == 'mes':
            relatorios = relatorios.filter(
                data_servico__year=date.today().year,
                data_servico__month=date.today().month
            )
    
    if busca:
        relatorios = relatorios.filter(
            Q(placa_veiculo__icontains=busca) |
            Q(modelo_veiculo__icontains=busca) |
            Q(local_servico__icontains=busca) |
            Q(observacoes__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(relatorios, 10)  # 10 relatórios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas rápidas
    total_relatorios = relatorios.count()
    relatorios_hoje = Relatorio.objects.filter(
        usuario=user,
        empresa=empresa,
        data_servico=date.today()
    ).count()
    
    context = {
        'relatorios': page_obj,
        'total_relatorios': total_relatorios,
        'relatorios_hoje': relatorios_hoje,
        'status_filter': status_filter,
        'data_filter': data_filter,
        'busca': busca,
        'empresa': empresa,
    }
    
    return render(request, 'reports/list.html', context)

@login_required
def relatorio_create(request):
    """Criar novo relatório"""
    user = request.user
    
    # Obter empresa ativa
    try:
        EmpresaAtivaUsuario = apps.get_model('dashboard', 'EmpresaAtivaUsuario')
        empresa_ativa = EmpresaAtivaUsuario.objects.get(usuario=user)
        empresa = empresa_ativa.empresa
    except Exception:
        messages.error(request, 'Nenhuma empresa ativa selecionada.')
        return redirect('core:home')
    
    if request.method == 'POST':
        try:
            # Criar novo relatório com dados do formulário
            relatorio = Relatorio(
                usuario=user,
                empresa=empresa,
                data_servico=request.POST.get('data_servico') or date.today(),
                
                # Campos de contagem
                ready_line=int(request.POST.get('ready_line', 0)),
                vip_line=int(request.POST.get('vip_line', 0)),
                overflow_kiosk=int(request.POST.get('overflow_kiosk', 0)),
                overflow_2=int(request.POST.get('overflow_2', 0)),
                black_top=int(request.POST.get('black_top', 0)),
                return_line=int(request.POST.get('return_line', 0)),
                mecanico=int(request.POST.get('mecanico', 0)),
                gas_run=int(request.POST.get('gas_run', 0)),
                
                forecasted_drops=int(request.POST.get('forecasted_drops', 0)),
                observacoes=request.POST.get('observacoes', ''),
                
                status='concluido'  # Já marca como concluído por padrão
            )
            
            relatorio.save()
            messages.success(request, f'Relatório criado com sucesso! Total: {relatorio.total_count_cleaned_cars} carros limpos.')
            return redirect('reports:detail', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar relatório: {str(e)}')
    
    # Dados para o formulário
    context = {
        'empresa': empresa,
        'data_hoje': date.today(),
    }
    
    return render(request, 'reports/create.html', context)

@login_required
def relatorio_detail(request, pk):
    """Visualizar detalhes de um relatório"""
    relatorio = get_object_or_404(
        Relatorio.objects.select_related('empresa'), 
        pk=pk,
        usuario=request.user
    )
    
    context = {
        'relatorio': relatorio,
    }
    
    return render(request, 'reports/detail.html', context)

@login_required
def relatorio_edit(request, pk):
    """Editar um relatório existente"""
    relatorio = get_object_or_404(
        Relatorio, 
        pk=pk,
        usuario=request.user
    )
    
    if request.method == 'POST':
        try:
            # Atualizar campos do relatório
            relatorio.data_servico = request.POST.get('data_servico') or relatorio.data_servico
            relatorio.placa_veiculo = request.POST.get('placa_veiculo', '').upper()
            relatorio.modelo_veiculo = request.POST.get('modelo_veiculo', '')
            relatorio.cor_veiculo = request.POST.get('cor_veiculo', '')
            relatorio.quilometragem = request.POST.get('quilometragem') or None
            relatorio.tipo_servico = request.POST.get('tipo_servico')
            relatorio.condicao_inicial = request.POST.get('condicao_inicial')
            relatorio.condicao_final = request.POST.get('condicao_final')
            relatorio.hora_inicio = request.POST.get('hora_inicio')
            relatorio.hora_fim = request.POST.get('hora_fim') or None
            relatorio.local_servico = request.POST.get('local_servico', '')
            relatorio.observacoes = request.POST.get('observacoes', '')
            relatorio.problemas_encontrados = request.POST.get('problemas_encontrados', '')
            relatorio.produtos_utilizados = request.POST.get('produtos_utilizados', '')
            relatorio.avaliacao_qualidade = request.POST.get('avaliacao_qualidade') or None
            
            relatorio.save()
            messages.success(request, 'Relatório atualizado com sucesso!')
            return redirect('reports:detail', pk=relatorio.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar relatório: {str(e)}')
    
    context = {
        'relatorio': relatorio,
        'tipos_servico': Relatorio.TIPO_SERVICO_CHOICES,
        'condicoes': Relatorio.CONDICAO_VEICULO_CHOICES,
    }
    
    return render(request, 'reports/edit.html', context)

@login_required
def relatorio_delete(request, pk):
    """Deletar um relatório"""
    relatorio = get_object_or_404(
        Relatorio,
        pk=pk,
        usuario=request.user
    )
    
    if request.method == 'POST':
        placa = relatorio.placa_veiculo
        relatorio.delete()
        messages.success(request, f'Relatório do veículo {placa} foi excluído.')
        return redirect('reports:list')
    
    context = {
        'relatorio': relatorio,
    }
    
    return render(request, 'reports/confirm_delete.html', context)