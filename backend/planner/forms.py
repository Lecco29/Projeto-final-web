"""
Formulários Django usando ModelForm para criar/editar registros.
"""

from django import forms
from .models import Ativo, HistoricoDividendo, MetaRenda


class AtivoForm(forms.ModelForm):
    """
    Formulário para criar e editar Ativos.
    """
    class Meta:
        model = Ativo
        fields = ['ticker', 'nome_empresa', 'setor', 'pais', 'observacoes']
        widgets = {
            'ticker': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: PETR4, VALE3'
            }),
            'nome_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da empresa'
            }),
            'setor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Petróleo, Mineração'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País de origem'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre o ativo'
            }),
        }
        labels = {
            'ticker': 'Ticker',
            'nome_empresa': 'Nome da Empresa',
            'setor': 'Setor',
            'pais': 'País',
            'observacoes': 'Observações',
        }

    def clean_ticker(self):
        """Validação: ticker deve ser em maiúsculas."""
        ticker = self.cleaned_data.get('ticker')
        if ticker:
            return ticker.upper().strip()
        return ticker


class HistoricoDividendoForm(forms.ModelForm):
    """
    Formulário para criar e editar histórico de dividendos.
    """
    class Meta:
        model = HistoricoDividendo
        fields = ['ativo', 'data_pagamento', 'valor_por_acao', 'fonte', 'observacoes']
        widgets = {
            'ativo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_pagamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'valor_por_acao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0',
                'placeholder': '0.0000'
            }),
            'fonte': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre este pagamento'
            }),
        }
        labels = {
            'ativo': 'Ativo',
            'data_pagamento': 'Data de Pagamento',
            'valor_por_acao': 'Valor por Ação (R$)',
            'fonte': 'Fonte',
            'observacoes': 'Observações',
        }


class MetaRendaForm(forms.ModelForm):
    """
    Formulário para criar e editar Metas de Renda.
    """
    class Meta:
        model = MetaRenda
        fields = [
            'nome',
            'renda_mensal_desejada',
            'anos_para_atingir',
            'inflacao_media_anual',
            'percentual_reinvestimento'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Independência Financeira'
            }),
            'renda_mensal_desejada': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'anos_para_atingir': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Ex: 10'
            }),
            'inflacao_media_anual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '4.5'
            }),
            'percentual_reinvestimento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0'
            }),
        }
        labels = {
            'nome': 'Nome da Meta',
            'renda_mensal_desejada': 'Renda Mensal Desejada (R$)',
            'anos_para_atingir': 'Anos para Atingir',
            'inflacao_media_anual': 'Inflação Média Anual (%)',
            'percentual_reinvestimento': 'Percentual de Reinvestimento (%)',
        }

    def clean_renda_mensal_desejada(self):
        """Validação: renda deve ser positiva."""
        renda = self.cleaned_data.get('renda_mensal_desejada')
        if renda and renda <= 0:
            raise forms.ValidationError('A renda mensal desejada deve ser maior que zero.')
        return renda

    def clean_anos_para_atingir(self):
        """Validação: anos deve ser pelo menos 1."""
        anos = self.cleaned_data.get('anos_para_atingir')
        if anos and anos < 1:
            raise forms.ValidationError('Deve ter pelo menos 1 ano para atingir a meta.')
        return anos

