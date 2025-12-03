"""
Lógica de negócio para cálculos de simulação de dividendos.

Esta camada separa a lógica de cálculo das views, seguindo boas práticas.
"""

from decimal import Decimal
from typing import Dict, Optional


# Calcula o patrimônio alvo e o aporte mensal necessário para atingir uma meta de renda mensal em dividendos.
def calcular_simulacao_dividendos(
    renda_mensal_desejada: Decimal,
    anos_para_atingir: int,
    inflacao_media_anual: Decimal,
    percentual_reinvestimento: Decimal,
    yield_medio: Optional[Decimal] = None
) -> Dict[str, Decimal]:
    # Usar yield padrão de 6% se não fornecido
    if yield_medio is None:
        yield_medio = Decimal('6.0')
    
    # Converter percentuais para decimais (4.5% -> 0.045)
    inflacao = inflacao_media_anual / Decimal('100')
    yield_dec = yield_medio / Decimal('100')
    reinvestimento = percentual_reinvestimento / Decimal('100')
    
    # Calcular renda mensal ajustada pela inflação (valor futuro)
    # Fórmula: Valor Futuro = Valor Presente * (1 + inflação) ^ anos
    renda_ajustada = renda_mensal_desejada * (
        (Decimal('1') + inflacao) ** anos_para_atingir
    )
    
    # Calcular renda anual ajustada
    renda_anual = renda_ajustada * Decimal('12')
    
    # Calcular patrimônio alvo necessário
    # Se o yield é 6% ao ano, para gerar R$ X por ano, preciso de R$ X / 0.06
    patrimonio = renda_anual / yield_dec
    
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
    taxa_mensal = yield_dec / Decimal('12')
    
    # Ajustar taxa considerando reinvestimento
    # Se reinveste 50%, o crescimento efetivo é maior
    taxa = taxa_mensal * (Decimal('1') + reinvestimento)
    
    # Calcular aporte mensal usando fórmula de anuidade
    if taxa > 0:
        fator = (Decimal('1') + taxa) ** meses
        aporte = patrimonio * taxa / (fator - Decimal('1'))
    else:
        # Se não há retorno, apenas divide o patrimônio pelo número de meses
        aporte = patrimonio / Decimal(str(meses))
    
    return {
        'patrimonio_alvo': patrimonio.quantize(Decimal('0.01')),
        'renda_mensal_ajustada': renda_ajustada.quantize(Decimal('0.01')),
        'aporte_mensal': aporte.quantize(Decimal('0.01')),
        'yield_medio_usado': yield_medio,
    }


# Calcula o yield médio baseado no histórico de dividendos dos ativos.
def calcular_yield_medio_ativos(lista_ativos: list) -> Optional[Decimal]:
    if not lista_ativos:
        return None
    
    yields = []
    for ativo in lista_ativos:
        total_dividendos = ativo.get('dividendos_anuais', Decimal('0'))
        preco = ativo.get('preco_medio')
        
        # Se não temos preço, não podemos calcular yield
        if preco and preco > 0:
            yield_calc = (total_dividendos / preco) * Decimal('100')
            yields.append(yield_calc)
    
    if not yields:
        return None
    
    # Retornar média dos yields
    yield_medio = sum(yields) / Decimal(str(len(yields)))
    return yield_medio.quantize(Decimal('0.01'))

