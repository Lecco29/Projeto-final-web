"""
Serializers do Django REST Framework para expor os modelos via API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ativo, HistoricoDividendo, MetaRenda, Simulacao


# Serializer para User (apenas leitura, para referências).
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


# Serializer para HistoricoDividendo.
class HistoricoDividendoSerializer(serializers.ModelSerializer):
    ativo_ticker = serializers.CharField(source='ativo.ticker', read_only=True)
    ativo_nome = serializers.CharField(source='ativo.nome_empresa', read_only=True)

    class Meta:
        model = HistoricoDividendo
        fields = [
            'id', 'ativo', 'ativo_ticker', 'ativo_nome',
            'data_pagamento', 'valor_por_acao', 'fonte', 'observacoes', 'data_criacao'
        ]
        read_only_fields = ['id', 'data_criacao']


# Serializer para Ativo.
class AtivoSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    historico_dividendos = HistoricoDividendoSerializer(many=True, read_only=True)
    total_dividendos_ano = serializers.SerializerMethodField()

    class Meta:
        model = Ativo
        fields = [
            'id', 'usuario', 'usuario_username', 'ticker', 'nome_empresa',
            'setor', 'pais', 'observacoes', 'data_criacao', 'data_atualizacao',
            'historico_dividendos', 'total_dividendos_ano'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']

    # Calcula o total de dividendos do último ano para este ativo.
    def get_total_dividendos_ano(self, obj):
        from datetime import datetime, timedelta
        from django.db.models import Sum
        
        um_ano_atras = datetime.now().date() - timedelta(days=365)
        total = obj.historico_dividendos.filter(
            data_pagamento__gte=um_ano_atras
        ).aggregate(Sum('valor_por_acao'))['valor_por_acao__sum']
        
        return float(total) if total else 0.0


# Serializer para MetaRenda.
class MetaRendaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    simulacoes = serializers.SerializerMethodField()

    class Meta:
        model = MetaRenda
        fields = [
            'id', 'usuario', 'usuario_username', 'nome', 'renda_mensal_desejada',
            'anos_para_atingir', 'inflacao_media_anual', 'percentual_reinvestimento',
            'data_criacao', 'data_atualizacao', 'simulacoes'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']

    # Retorna as últimas 5 simulações desta meta.
    def get_simulacoes(self, obj):
        simulacoes = obj.simulacoes.all()[:5]
        return SimulacaoSerializer(simulacoes, many=True).data


# Serializer para Simulacao.
class SimulacaoSerializer(serializers.ModelSerializer):
    meta_renda_nome = serializers.CharField(source='meta_renda.nome', read_only=True)

    class Meta:
        model = Simulacao
        fields = [
            'id', 'meta_renda', 'meta_renda_nome', 'patrimonio_alvo',
            'aporte_mensal', 'yield_medio_usado', 'data_execucao', 'observacoes'
        ]
        read_only_fields = ['id', 'data_execucao']

