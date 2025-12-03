"""
Configuração do Django Admin para facilitar testes e gerenciamento.
"""

from django.contrib import admin
from .models import Ativo, HistoricoDividendo, MetaRenda, Simulacao


# Configuração do Django Admin para Ativo.
@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ['ticker', 'nome_empresa', 'setor', 'usuario', 'data_criacao']
    list_filter = ['setor', 'pais', 'usuario']
    search_fields = ['ticker', 'nome_empresa', 'setor']


# Configuração do Django Admin para HistoricoDividendo.
@admin.register(HistoricoDividendo)
class HistoricoDividendoAdmin(admin.ModelAdmin):
    list_display = ['ativo', 'data_pagamento', 'valor_por_acao', 'fonte']
    list_filter = ['fonte', 'data_pagamento', 'ativo']
    search_fields = ['ativo__ticker', 'ativo__nome_empresa']
    date_hierarchy = 'data_pagamento'


# Configuração do Django Admin para MetaRenda.
@admin.register(MetaRenda)
class MetaRendaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'renda_mensal_desejada', 'anos_para_atingir', 'usuario', 'data_criacao']
    list_filter = ['usuario', 'data_criacao']
    search_fields = ['nome']


# Configuração do Django Admin para Simulacao.
@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ['meta_renda', 'patrimonio_alvo', 'aporte_mensal', 'data_execucao']
    list_filter = ['data_execucao', 'meta_renda']
    search_fields = ['meta_renda__nome']

