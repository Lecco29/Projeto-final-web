"""
URLs da API REST para o app planner.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AtivoViewSet,
    HistoricoDividendoViewSet,
    MetaRendaViewSet,
    SimulacaoViewSet
)

# Criar router do DRF
router = DefaultRouter()
router.register(r'ativos', AtivoViewSet, basename='ativo')
router.register(r'historico-dividendos', HistoricoDividendoViewSet, basename='historico-dividendo')
router.register(r'metas-renda', MetaRendaViewSet, basename='meta-renda')
router.register(r'simulacoes', SimulacaoViewSet, basename='simulacao')

urlpatterns = [
    path('', include(router.urls)),
]

