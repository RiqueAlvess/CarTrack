from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
from datetime import date

@login_required
def home_view(request):
    user = request.user
    
    # Dados para o contexto
    context = {
        'relatorios_hoje': 0,
        'ultimo_envio': None,
        'empresa': None,
    }
    
    try:
        # Tentar obter empresa ativa
        EmpresaAtivaUsuario = apps.get_model('dashboard', 'EmpresaAtivaUsuario')
        empresa_ativa = EmpresaAtivaUsuario.objects.get(usuario=user)
        context['empresa'] = empresa_ativa.empresa
        
        # Importar model de relatórios aqui para evitar circular import
        try:
            Relatorio = apps.get_model('reports', 'Relatorio')
            
            # Estatísticas de relatórios
            relatorios_hoje = Relatorio.objects.filter(
                usuario=user,
                empresa=empresa_ativa.empresa,
                data_servico=date.today()
            ).count()
            
            context['relatorios_hoje'] = relatorios_hoje
            
            # Último relatório enviado
            ultimo_enviado = Relatorio.objects.filter(
                usuario=user,
                empresa=empresa_ativa.empresa,
                status='enviado'
            ).order_by('-data_atualizacao').first()
            
            if ultimo_enviado:
                context['ultimo_envio'] = {
                    'data': ultimo_enviado.data_servico,
                    'hora': ultimo_enviado.data_atualizacao.time(),
                    'placa': ultimo_enviado.placa_veiculo
                }
        
        except Exception:
            # Model de relatórios não existe ainda ou outro erro
            pass
    
    except Exception:
        # Usuário não tem empresa ativa selecionada ou outro erro
        pass
    
    return render(request, 'core/home.html', context)