"""
Modelos Django para o sistema de planejamento de dividendos.

Relacionamentos:
- Usuario (User padrão do Django) -> Ativo (um-para-muitos)
- Ativo -> HistoricoDividendo (um-para-muitos)
- Usuario -> MetaRenda (um-para-muitos)
- MetaRenda -> Simulacao (um-para-muitos)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Representa um ativo (ação/ticker) que o usuário possui ou acompanha, com relacionamento muitos-para-um com User.
class Ativo(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ativos',
        verbose_name='Usuário'
    )
    ticker = models.CharField(
        max_length=20,
        verbose_name='Ticker',
        help_text='Código do ativo (ex: PETR4, VALE3)'
    )
    nome_empresa = models.CharField(
        max_length=200,
        verbose_name='Nome da Empresa'
    )
    setor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Setor',
        help_text='Setor da empresa (ex: Petróleo, Mineração)'
    )
    pais = models.CharField(
        max_length=100,
        default='Brasil',
        verbose_name='País'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )

    class Meta:
        verbose_name = 'Ativo'
        verbose_name_plural = 'Ativos'
        ordering = ['ticker']
        # Garantir que um usuário não tenha ativos duplicados com o mesmo ticker
        unique_together = ['usuario', 'ticker']

    # Retorna representação string do ativo.
    def __str__(self):
        return f"{self.ticker} - {self.nome_empresa}"


# Representa um registro histórico de pagamento de dividendos, com relacionamento muitos-para-um com Ativo.
class HistoricoDividendo(models.Model):
    
    FONTE_CHOICES = [
        ('manual', 'Manual'),
        ('api', 'API'),
    ]

    ativo = models.ForeignKey(
        Ativo,
        on_delete=models.CASCADE,
        related_name='historico_dividendos',
        verbose_name='Ativo'
    )
    data_pagamento = models.DateField(
        verbose_name='Data de Pagamento'
    )
    valor_por_acao = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(0)],
        verbose_name='Valor por Ação (R$)',
        help_text='Valor do dividendo pago por ação'
    )
    fonte = models.CharField(
        max_length=10,
        choices=FONTE_CHOICES,
        default='manual',
        verbose_name='Fonte'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Histórico de Dividendo'
        verbose_name_plural = 'Históricos de Dividendos'
        ordering = ['-data_pagamento', '-data_criacao']

    # Retorna representação string do histórico de dividendo.
    def __str__(self):
        return f"{self.ativo.ticker} - {self.data_pagamento} - R$ {self.valor_por_acao}"


# Representa uma meta de renda mensal desejada, com relacionamento muitos-para-um com User.
class MetaRenda(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='metas_renda',
        verbose_name='Usuário'
    )
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome da Meta',
        help_text='Nome descritivo para esta meta (ex: Independência Financeira)'
    )
    renda_mensal_desejada = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Renda Mensal Desejada (R$)',
        help_text='Valor da renda mensal que deseja receber em dividendos'
    )
    anos_para_atingir = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Anos para Atingir',
        help_text='Quantos anos você tem para atingir esta meta'
    )
    inflacao_media_anual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=4.5,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Inflação Média Anual (%)',
        help_text='Percentual de inflação média anual esperada'
    )
    percentual_reinvestimento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Percentual de Reinvestimento (%)',
        help_text='Percentual dos dividendos que serão reinvestidos'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Atualização'
    )

    class Meta:
        verbose_name = 'Meta de Renda'
        verbose_name_plural = 'Metas de Renda'
        ordering = ['-data_criacao']

    # Retorna representação string da meta de renda.
    def __str__(self):
        return f"{self.nome} - R$ {self.renda_mensal_desejada}/mês"


# Armazena resultados de simulações realizadas, com relacionamento muitos-para-um com MetaRenda.
class Simulacao(models.Model):
    meta_renda = models.ForeignKey(
        MetaRenda,
        on_delete=models.CASCADE,
        related_name='simulacoes',
        verbose_name='Meta de Renda'
    )
    patrimonio_alvo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Patrimônio Alvo (R$)',
        help_text='Patrimônio necessário para atingir a meta'
    )
    aporte_mensal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Aporte Mensal Necessário (R$)',
        help_text='Valor que precisa investir mensalmente'
    )
    yield_medio_usado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Yield Médio Usado (%)',
        help_text='Yield médio utilizado no cálculo'
    )
    data_execucao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Execução'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )

    class Meta:
        verbose_name = 'Simulação'
        verbose_name_plural = 'Simulações'
        ordering = ['-data_execucao']

    # Retorna representação string da simulação.
    def __str__(self):
        return f"Simulação {self.meta_renda.nome} - {self.data_execucao.strftime('%d/%m/%Y %H:%M')}"

