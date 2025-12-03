"""
Views/API REST para CRUD completo de todas as entidades e busca.

Todas as operações CRUD e busca são implementadas aqui, não no Django Admin.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import requests

from .models import Ativo, HistoricoDividendo, MetaRenda, Simulacao
from .serializers import (
    AtivoSerializer, HistoricoDividendoSerializer,
    MetaRendaSerializer, SimulacaoSerializer
)
from .services import calcular_simulacao_dividendos, calcular_yield_medio_ativos
from .brapi_service import BrapiService


class AtivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Ativos.
    Inclui busca por ticker ou nome.
    """
    serializer_class = AtivoSerializer
    # permission_classes = [IsAuthenticated]  # Desabilitado para facilitar testes

    def get_queryset(self):
        """Filtra ativos do usuário logado."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user_id = self.request.user.id if self.request.user.is_authenticated else 1
        queryset = Ativo.objects.filter(usuario_id=user_id)
        
        # Busca por ticker ou nome
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(ticker__icontains=search) |
                Q(nome_empresa__icontains=search) |
                Q(setor__icontains=search)
            )
        
        return queryset.order_by('ticker')

    def perform_create(self, serializer):
        """Associa o ativo ao usuário logado ao criar."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user = self.request.user if self.request.user.is_authenticated else User.objects.get(id=1)
        serializer.save(usuario=user)
    
    @action(detail=False, methods=['post'])
    def buscar_dados_brapi(self, request):
        """
        Busca dados de uma ação na API Brapi e retorna informações.
        Endpoint: POST /api/ativos/buscar_dados_brapi/
        Body: {"ticker": "PETR4"}
        """
        ticker = request.data.get('ticker', '').upper().strip()
        
        if not ticker:
            return Response(
                {'erro': 'Ticker é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Buscar dados na Brapi
            quote_data = BrapiService.get_quote(ticker, range_days="1y", dividends=True)
            
            if not quote_data:
                # Verificar se é um ticker que requer token
                tickers_gratuitos = ["PETR4", "MGLU3", "VALE3", "ITUB4"]
                if ticker.upper() not in tickers_gratuitos:
                    erro_msg = f'Não foi possível encontrar dados para o ticker {ticker}. Este ticker requer um token de autenticação da Brapi. Tickers gratuitos disponíveis: PETR4, MGLU3, VALE3, ITUB4. Para obter um token gratuito e acessar outros tickers, acesse: https://brapi.dev'
                else:
                    erro_msg = f'Não foi possível encontrar dados para o ticker {ticker}. Verifique se o ticker está correto e tente novamente. A API pode estar temporariamente indisponível.'
                
                return Response(
                    {'erro': erro_msg},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Extrair informações diretamente do quote_data para evitar múltiplas chamadas
            nome_empresa = quote_data.get("longName") or quote_data.get("shortName") or ""
            setor = quote_data.get("sector") or ""
            preco_atual = quote_data.get("regularMarketPrice") or quote_data.get("price")
            
            # Validar que temos dados básicos
            if not nome_empresa and not preco_atual:
                return Response(
                    {'erro': f'Dados incompletos recebidos da Brapi para {ticker}. Tente novamente.'},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            # Buscar dividendos e yield
            try:
                dividends = BrapiService.get_dividends(ticker, range_days="1y")
                print(f"Dividendos obtidos: {len(dividends) if dividends else 0}")
            except Exception as e:
                print(f"Erro ao buscar dividendos: {e}")
                import traceback
                traceback.print_exc()
                dividends = []
            
            # Converter dividendos para formato serializável (Decimal -> float)
            dividends_serialized = []
            for div in dividends:
                try:
                    valor_acao = div.get("valor_por_acao", 0)
                    # Converter Decimal para float de forma segura
                    if isinstance(valor_acao, Decimal):
                        valor_acao = float(valor_acao)
                    elif not isinstance(valor_acao, (int, float)):
                        valor_acao = float(str(valor_acao)) if valor_acao else 0.0
                    else:
                        valor_acao = float(valor_acao)
                    
                    dividends_serialized.append({
                        "data_pagamento": str(div.get("data_pagamento", "")),
                        "valor_por_acao": valor_acao,
                        "fonte": str(div.get("fonte", "api"))
                    })
                except Exception as e:
                    print(f"Erro ao serializar dividendo: {e}, div: {div}")
                    continue
            
            yield_value = None
            if preco_atual:
                try:
                    current_price = Decimal(str(preco_atual))
                    if dividends and len(dividends) > 0:
                        # Usar os dividendos originais (não serializados) para calcular yield
                        total_dividends = sum(Decimal(str(d.get("valor_por_acao", 0))) for d in dividends)
                        if total_dividends > 0 and current_price > 0:
                            yield_value = (total_dividends / current_price) * Decimal("100")
                            print(f"Yield calculado: {yield_value}")
                except Exception as e:
                    print(f"Erro ao calcular yield: {e}")
                    import traceback
                    traceback.print_exc()
                    yield_value = None
            
            # Preparar resposta com conversões seguras
            try:
                response_data = {
                    'ticker': str(ticker),
                    'nome_empresa': str(nome_empresa) if nome_empresa else '',
                    'setor': str(setor) if setor else '',
                    'pais': 'Brasil',
                    'preco_atual': float(preco_atual) if preco_atual else None,
                    'yield_anual': float(yield_value) if yield_value else None,
                    'dividendos': dividends_serialized,
                    'total_dividendos_ano': len(dividends_serialized),
                }
                
                # Log para debug (remover em produção)
                print(f"Retornando dados da Brapi para {ticker}: {len(dividends_serialized)} dividendos")
                
                return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                print(f"Erro ao preparar resposta: {e}")
                traceback.print_exc()
                return Response(
                    {'erro': f'Erro ao processar resposta: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except requests.exceptions.Timeout:
            return Response(
                {'erro': 'Timeout ao conectar com a API Brapi. Tente novamente em alguns instantes.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {'erro': 'Erro de conexão com a API Brapi. Verifique sua conexão com a internet.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"Erro completo ao buscar dados da Brapi: {error_trace}")
            
            # Log detalhado para debug
            print(f"Tipo do erro: {type(e).__name__}")
            print(f"Mensagem: {error_msg}")
            
            if 'Network' in error_msg or 'connection' in error_msg.lower():
                error_msg = 'Erro de conexão. Verifique sua internet e se a API Brapi está disponível.'
            elif '500' in error_msg or 'Internal Server Error' in error_msg:
                error_msg = 'Erro interno ao processar dados da Brapi. Tente novamente ou use um ticker diferente.'
            elif isinstance(e, (ValueError, TypeError)):
                error_msg = f'Erro ao processar dados: {error_msg}'
            
            return Response(
                {'erro': f'Erro ao buscar dados da Brapi: {error_msg}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def importar_dividendos_brapi(self, request, pk=None):
        """
        Importa dividendos de um ativo da API Brapi.
        Endpoint: POST /api/ativos/{id}/importar_dividendos_brapi/
        """
        ativo = self.get_object()
        
        # Buscar dividendos na Brapi
        dividends = BrapiService.get_dividends(ativo.ticker, range_days="1y")
        
        if not dividends:
            return Response(
                {'erro': f'Não foram encontrados dividendos para {ativo.ticker}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Importar dividendos (evitar duplicatas)
        importados = 0
        duplicados = 0
        
        for div_data in dividends:
            # Verificar se já existe
            existe = HistoricoDividendo.objects.filter(
                ativo=ativo,
                data_pagamento=div_data['data_pagamento']
            ).exists()
            
            if not existe:
                HistoricoDividendo.objects.create(
                    ativo=ativo,
                    data_pagamento=div_data['data_pagamento'],
                    valor_por_acao=div_data['valor_por_acao'],
                    fonte=div_data['fonte'],
                    observacoes=f'Importado automaticamente da Brapi em {timezone.now().strftime("%d/%m/%Y %H:%M")}'
                )
                importados += 1
            else:
                duplicados += 1
        
        return Response({
            'mensagem': f'Importação concluída para {ativo.ticker}',
            'importados': importados,
            'duplicados': duplicados,
            'total_encontrados': len(dividends)
        }, status=status.HTTP_200_OK)


class HistoricoDividendoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Histórico de Dividendos.
    Inclui filtros por ativo e intervalo de datas.
    """
    serializer_class = HistoricoDividendoSerializer
    # permission_classes = [IsAuthenticated]  # Desabilitado para facilitar testes

    def get_queryset(self):
        """Filtra dividendos dos ativos do usuário logado."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user_id = self.request.user.id if self.request.user.is_authenticated else 1
        ativos_usuario = Ativo.objects.filter(usuario_id=user_id)
        queryset = HistoricoDividendo.objects.filter(ativo__in=ativos_usuario)
        
        # Filtro por ativo
        ativo_id = self.request.query_params.get('ativo', None)
        if ativo_id:
            queryset = queryset.filter(ativo_id=ativo_id)
        
        # Filtro por data inicial
        data_inicio = self.request.query_params.get('data_inicio', None)
        if data_inicio:
            try:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(data_pagamento__gte=data_inicio)
            except ValueError:
                pass
        
        # Filtro por data final
        data_fim = self.request.query_params.get('data_fim', None)
        if data_fim:
            try:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                queryset = queryset.filter(data_pagamento__lte=data_fim)
            except ValueError:
                pass
        
        return queryset.order_by('-data_pagamento', '-data_criacao')


class MetaRendaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Metas de Renda.
    Inclui busca por nome ou valor de renda.
    """
    serializer_class = MetaRendaSerializer
    # permission_classes = [IsAuthenticated]  # Desabilitado para facilitar testes

    def get_queryset(self):
        """Filtra metas do usuário logado."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user_id = self.request.user.id if self.request.user.is_authenticated else 1
        queryset = MetaRenda.objects.filter(usuario_id=user_id)
        
        # Busca por nome
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(renda_mensal_desejada__gte=Decimal(search)) if search.replace('.', '').isdigit() else Q()
            )
        
        return queryset.order_by('-data_criacao')

    def perform_create(self, serializer):
        """Associa a meta ao usuário logado ao criar."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user = self.request.user if self.request.user.is_authenticated else User.objects.get(id=1)
        serializer.save(usuario=user)

    @action(detail=True, methods=['post'])
    def simular(self, request, pk=None):
        """
        Endpoint para executar uma simulação baseada em uma MetaRenda.
        Aceita yield_medio opcional e lista de ativos_ids.
        Se não fornecido, calcula baseado nos ativos selecionados ou do usuário.
        """
        meta = self.get_object()
        
        # Obter yield médio (opcional)
        yield_medio = request.data.get('yield_medio', None)
        if yield_medio:
            try:
                yield_medio = Decimal(str(yield_medio))
            except (ValueError, TypeError):
                yield_medio = None
        
        # Obter lista de ativos selecionados (opcional)
        ativos_ids = request.data.get('ativos_ids', [])
        user_id = request.user.id if request.user.is_authenticated else 1
        
        # Se não fornecido, tentar calcular baseado nos ativos selecionados ou do usuário
        if yield_medio is None:
            if ativos_ids:
                # Usar apenas os ativos selecionados
                ativos = Ativo.objects.filter(id__in=ativos_ids, usuario_id=user_id)
            else:
                # Usar todos os ativos do usuário
                ativos = Ativo.objects.filter(usuario_id=user_id)
            
            yields = []
            
            for ativo in ativos:
                # Tentar buscar yield da Brapi
                try:
                    yield_ativo = BrapiService.calculate_yield(ativo.ticker, range_days="1y")
                    if yield_ativo:
                        yields.append(yield_ativo)
                except Exception as e:
                    print(f"Erro ao buscar yield de {ativo.ticker}: {e}")
                    # Se falhar, calcular baseado nos dividendos locais
                    um_ano_atras = timezone.now().date() - timedelta(days=365)
                    dividendos = HistoricoDividendo.objects.filter(
                        ativo=ativo,
                        data_pagamento__gte=um_ano_atras
                    )
                    total_dividendos = sum(d.valor_por_acao for d in dividendos)
                    
                    if total_dividendos > 0:
                        # Tentar buscar preço atual da Brapi
                        preco = BrapiService.get_current_price(ativo.ticker)
                        if preco and preco > 0:
                            yield_calculado = (total_dividendos / preco) * Decimal('100')
                            yields.append(yield_calculado)
            
            # Calcular média dos yields ou usar padrão
            if yields:
                yield_medio = sum(yields) / Decimal(str(len(yields)))
            else:
                yield_medio = Decimal('6.0')  # Padrão se não conseguir calcular
        
        # Executar simulação
        resultado = calcular_simulacao_dividendos(
            renda_mensal_desejada=meta.renda_mensal_desejada,
            anos_para_atingir=meta.anos_para_atingir,
            inflacao_media_anual=meta.inflacao_media_anual,
            percentual_reinvestimento=meta.percentual_reinvestimento,
            yield_medio=yield_medio
        )
        
        # Salvar simulação (opcional)
        salvar = request.data.get('salvar', False)
        if salvar:
            Simulacao.objects.create(
                meta_renda=meta,
                patrimonio_alvo=resultado['patrimonio_alvo'],
                aporte_mensal=resultado['aporte_mensal'],
                yield_medio_usado=resultado['yield_medio_usado'],
                observacoes=request.data.get('observacoes', '')
            )
        
        return Response(resultado, status=status.HTTP_200_OK)


class SimulacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de Simulações.
    """
    serializer_class = SimulacaoSerializer
    # permission_classes = [IsAuthenticated]  # Desabilitado para facilitar testes

    def get_queryset(self):
        """Filtra simulações das metas do usuário logado."""
        # Por enquanto, usar usuário padrão (id=1) se não autenticado
        user_id = self.request.user.id if self.request.user.is_authenticated else 1
        metas_usuario = MetaRenda.objects.filter(usuario_id=user_id)
        queryset = Simulacao.objects.filter(meta_renda__in=metas_usuario)
        
        # Filtro por meta
        meta_id = self.request.query_params.get('meta', None)
        if meta_id:
            queryset = queryset.filter(meta_renda_id=meta_id)
        
        return queryset.order_by('-data_execucao')

