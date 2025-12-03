"""
Lógica de negócio para cálculos de simulação de dividendos.

Esta camada separa a lógica de cálculo das views, seguindo boas práticas.
"""

from decimal import Decimal
from typing import Dict, Optional


def calcular_simulacao_dividendos(
    renda_mensal_desejada: Decimal,
    anos_para_atingir: int,
    inflacao_media_anual: Decimal,
    percentual_reinvestimento: Decimal,
    yield_medio: Optional[Decimal] = None
) -> Dict[str, Decimal]:
    """
    Calcula o patrimônio alvo e o aporte mensal necessário para atingir
    uma meta de renda mensal em dividendos.

    Parâmetros:
    -----------
    renda_mensal_desejada : Decimal
        Renda mensal desejada em reais (valor atual)
    anos_para_atingir : int
        Quantidade de anos para atingir a meta
    inflacao_media_anual : Decimal
        Inflação média anual esperada (em percentual, ex: 4.5 para 4.5%)
    percentual_reinvestimento : Decimal
        Percentual dos dividendos que serão reinvestidos (em percentual, ex: 50 para 50%)
    yield_medio : Decimal, opcional
        Yield médio esperado dos investimentos (em percentual, ex: 6.0 para 6%)
        Se não fornecido, usa um padrão de 6%

    Retorna:
    --------
    Dict com:
        - patrimonio_alvo: Patrimônio necessário para gerar a renda desejada
        - renda_mensal_ajustada: Renda mensal ajustada pela inflação
        - aporte_mensal: Aporte mensal necessário
        - yield_medio_usado: Yield médio utilizado no cálculo
    """
    # Usar yield padrão de 6% se não fornecido
    if yield_medio is None:
        yield_medio = Decimal('6.0')
    
    # Converter percentuais para decimais (4.5% -> 0.045)
    inflacao_decimal = inflacao_media_anual / Decimal('100')
    yield_decimal = yield_medio / Decimal('100')
    reinvestimento_decimal = percentual_reinvestimento / Decimal('100')
    
    # Calcular renda mensal ajustada pela inflação (valor futuro)
    # Fórmula: Valor Futuro = Valor Presente * (1 + inflação) ^ anos
    renda_mensal_ajustada = renda_mensal_desejada * (
        (Decimal('1') + inflacao_decimal) ** anos_para_atingir
    )
    
    # Calcular renda anual ajustada
    renda_anual_ajustada = renda_mensal_ajustada * Decimal('12')
    
    # Calcular patrimônio alvo necessário
    # Se o yield é 6% ao ano, para gerar R$ X por ano, preciso de R$ X / 0.06
    patrimonio_alvo = renda_anual_ajustada / yield_decimal
    
    # Calcular aporte mensal necessário
    # Considerando reinvestimento dos dividendos, o crescimento é acelerado
    # Usando fórmula de valor futuro de anuidade com crescimento:
    # FV = PMT * [((1 + r)^n - 1) / r]
    # Onde:
    # - FV = valor futuro (patrimônio alvo)
    # - PMT = pagamento periódico (aporte mensal)
    # - r = taxa de retorno mensal (yield anual / 12)
    # - n = número de períodos (meses)
    
    meses = anos_para_atingir * 12
    taxa_mensal = yield_decimal / Decimal('12')
    
    # Ajustar taxa considerando reinvestimento
    # Se reinveste 50%, o crescimento efetivo é maior
    taxa_efetiva_mensal = taxa_mensal * (Decimal('1') + reinvestimento_decimal)
    
    # Calcular aporte mensal usando fórmula de anuidade
    if taxa_efetiva_mensal > 0:
        fator_crescimento = (Decimal('1') + taxa_efetiva_mensal) ** meses
        aporte_mensal = patrimonio_alvo * taxa_efetiva_mensal / (fator_crescimento - Decimal('1'))
    else:
        # Se não há retorno, apenas divide o patrimônio pelo número de meses
        aporte_mensal = patrimonio_alvo / Decimal(str(meses))
    
    return {
        'patrimonio_alvo': patrimonio_alvo.quantize(Decimal('0.01')),
        'renda_mensal_ajustada': renda_mensal_ajustada.quantize(Decimal('0.01')),
        'aporte_mensal': aporte_mensal.quantize(Decimal('0.01')),
        'yield_medio_usado': yield_medio,
    }


def calcular_yield_medio_ativos(ativos_com_dividendos: list) -> Optional[Decimal]:
    """
    Calcula o yield médio baseado no histórico de dividendos dos ativos.

    Parâmetros:
    -----------
    ativos_com_dividendos : list
        Lista de dicionários com informações dos ativos e seus dividendos.
        Cada dicionário deve ter:
        - 'ticker': str
        - 'dividendos_anuais': Decimal (soma dos dividendos do último ano)
        - 'preco_medio': Decimal (preço médio da ação, opcional)

    Retorna:
    --------
    Decimal com o yield médio em percentual, ou None se não houver dados suficientes.
    """
    if not ativos_com_dividendos:
        return None
    
    yields = []
    for ativo in ativos_com_dividendos:
        dividendos_anuais = ativo.get('dividendos_anuais', Decimal('0'))
        preco_medio = ativo.get('preco_medio')
        
        # Se não temos preço médio, não podemos calcular yield
        if preco_medio and preco_medio > 0:
            yield_ativo = (dividendos_anuais / preco_medio) * Decimal('100')
            yields.append(yield_ativo)
    
    if not yields:
        return None
    
    # Retornar média dos yields
    yield_medio = sum(yields) / Decimal(str(len(yields)))
    return yield_medio.quantize(Decimal('0.01'))

