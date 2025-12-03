"""
Serviço para consumir a API Brapi (brapi.dev) e buscar dados de ações brasileiras.
"""

import requests
import os
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta


class BrapiService:
    """
    Classe para interagir com a API Brapi.
    Documentação: https://brapi.dev/docs
    
    Nota: Alguns tickers são gratuitos (PETR4, MGLU3, VALE3, ITUB4).
    Para outros tickers, é necessário um token de autenticação.
    Obtenha um token gratuito em: https://brapi.dev
    """
    
    BASE_URL = "https://brapi.dev/api"
    
    # Tickers gratuitos que não precisam de token
    FREE_TICKERS = ["PETR4", "MGLU3", "VALE3", "ITUB4"]
    
    @staticmethod
    def test_connection() -> bool:
        """Testa se a conexão com a Brapi está funcionando."""
        try:
            response = requests.get("https://brapi.dev/api/quote/PETR4", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def get_quote(ticker: str, range_days: str = "1y", dividends: bool = True) -> Optional[Dict]:
        """
        Busca informações de uma ação, incluindo preço e dividendos.
        
        Args:
            ticker: Código do ativo (ex: PETR4, VALE3)
            range_days: Período para histórico (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            dividends: Se True, inclui dados de dividendos
        
        Returns:
            Dict com dados da ação ou None em caso de erro
        """
        try:
            # Formatar ticker corretamente (remover espaços, garantir maiúsculas)
            ticker = ticker.upper().strip()
            
            url = f"{BrapiService.BASE_URL}/quote/{ticker}"
            params = {
                "range": range_days,
                "dividends": "true" if dividends else "false"
            }
            
            # Adicionar token se disponível (pode ser configurado via variável de ambiente)
            # Para obter um token gratuito: https://brapi.dev
            token = os.environ.get('BRAPI_TOKEN', '')
            if token:
                params['token'] = token
            
            # Adicionar headers para evitar problemas
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15, verify=True)
            
            # Verificar status code
            if response.status_code == 401:
                if ticker.upper() not in BrapiService.FREE_TICKERS:
                    print(f"Erro 401: O ticker {ticker} requer autenticação. Alguns tickers são gratuitos (PETR4, MGLU3, VALE3, ITUB4). Para outros, obtenha um token gratuito em https://brapi.dev")
                else:
                    print(f"Erro 401: Problema de autenticação com a API Brapi para {ticker}")
                return None
            
            if response.status_code == 404:
                print(f"Ticker {ticker} não encontrado na Brapi")
                return None
            
            # Verificar outros erros HTTP antes de processar JSON
            if response.status_code != 200:
                print(f"Erro HTTP {response.status_code} da API Brapi para {ticker}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error") or error_data.get("message", f"Erro HTTP {response.status_code}")
                    print(f"Detalhes: {error_msg}")
                except:
                    print(f"Resposta: {response.text[:200]}")
                return None
            
            # Verificar se há erro na resposta JSON
            try:
                data = response.json()
                
                # Verificar se há mensagem de erro
                if "error" in data or "message" in data:
                    error_msg = data.get("error") or data.get("message", "Erro desconhecido")
                    print(f"Erro da API Brapi para {ticker}: {error_msg}")
                    return None
                
                # A API retorna um array de resultados
                if "results" in data and len(data["results"]) > 0:
                    return data["results"][0]
                
                # Se não tem results, pode ser que retornou diretamente
                if isinstance(data, dict) and "symbol" in data:
                    return data
                
                # Se chegou aqui e não retornou nada, não encontrou dados
                print(f"Nenhum dado encontrado na resposta da Brapi para {ticker}")
                return None
            except ValueError as e:
                # Resposta não é JSON válido
                print(f"Resposta inválida da API Brapi para {ticker}: {e}")
                print(f"Resposta recebida: {response.text[:200]}")
                return None
            
        except requests.exceptions.Timeout:
            print(f"Timeout ao buscar dados da Brapi para {ticker}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Erro de conexão ao buscar dados da Brapi para {ticker}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da Brapi para {ticker}: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao buscar dados da Brapi: {e}")
            return None
    
    @staticmethod
    def get_dividends(ticker: str, range_days: str = "1y") -> List[Dict]:
        """
        Extrai e formata os dividendos de uma ação.
        
        Args:
            ticker: Código do ativo
            range_days: Período para histórico
        
        Returns:
            Lista de dicionários com dados de dividendos formatados
        """
        quote_data = BrapiService.get_quote(ticker, range_days, dividends=True)
        
        if not quote_data:
            return []
        
        dividends = []
        
        # A API retorna dividendos no formato:
        # "dividendsData": {
        #   "cashDividends": [{"paymentDate": "2024-01-15T00:00:00.000Z", "rate": 0.50}, ...],
        #   "stockDividends": [...],
        #   "subscriptions": [...]
        # }
        if "dividendsData" in quote_data:
            dividends_data = quote_data["dividendsData"]
            
            # Novo formato: dividendsData é um objeto com cashDividends
            if isinstance(dividends_data, dict):
                cash_dividends = dividends_data.get("cashDividends", [])
                
                for div in cash_dividends:
                    try:
                        if not isinstance(div, dict):
                            continue
                        
                        # Extrair data de pagamento
                        payment_date = div.get("paymentDate", "")
                        if payment_date:
                            # Converter de ISO 8601 para formato YYYY-MM-DD
                            if isinstance(payment_date, str):
                                # Remover timezone e pegar apenas a data
                                date_str = payment_date.split('T')[0] if 'T' in payment_date else payment_date
                            else:
                                date_str = str(payment_date)
                        else:
                            continue
                        
                        # Extrair valor do dividendo (rate)
                        dividend_value = div.get("rate", 0)
                        
                        # Converter para Decimal
                        if isinstance(dividend_value, (int, float)):
                            dividend_value = Decimal(str(dividend_value))
                        else:
                            dividend_value = Decimal(str(dividend_value)) if dividend_value else Decimal('0')
                        
                        if date_str and dividend_value > 0:
                            dividends.append({
                                "data_pagamento": date_str,
                                "valor_por_acao": dividend_value,
                                "fonte": "api"
                            })
                    except Exception as e:
                        print(f"Erro ao processar dividendo: {e}")
                        continue
            
            # Formato antigo (compatibilidade): dividendsData é uma lista direta
            elif isinstance(dividends_data, list):
                for div in dividends_data:
                    try:
                        if not isinstance(div, dict):
                            continue
                        
                        date_str = div.get("date", "")
                        dividend_value = div.get("dividend", 0)
                        
                        if isinstance(dividend_value, (int, float)):
                            dividend_value = Decimal(str(dividend_value))
                        else:
                            dividend_value = Decimal(str(dividend_value)) if dividend_value else Decimal('0')
                        
                        if date_str and dividend_value > 0:
                            dividends.append({
                                "data_pagamento": date_str,
                                "valor_por_acao": dividend_value,
                                "fonte": "api"
                            })
                    except Exception as e:
                        print(f"Erro ao processar dividendo: {e}")
                        continue
        
        return dividends
    
    @staticmethod
    def get_current_price(ticker: str) -> Optional[Decimal]:
        """
        Busca o preço atual de uma ação.
        
        Args:
            ticker: Código do ativo
        
        Returns:
            Preço atual ou None
        """
        quote_data = BrapiService.get_quote(ticker, range_days="1d", dividends=False)
        
        if not quote_data:
            return None
        
        # A API retorna o preço em "regularMarketPrice" ou "price"
        price = quote_data.get("regularMarketPrice") or quote_data.get("price")
        
        if price:
            try:
                return Decimal(str(price))
            except:
                return None
        
        return None
    
    @staticmethod
    def calculate_yield(ticker: str, range_days: str = "1y") -> Optional[Decimal]:
        """
        Calcula o yield (dividend yield) de uma ação baseado nos dividendos do último ano.
        
        Args:
            ticker: Código do ativo
            range_days: Período para cálculo (recomendado: "1y")
        
        Returns:
            Yield em percentual ou None
        """
        quote_data = BrapiService.get_quote(ticker, range_days, dividends=True)
        
        if not quote_data:
            return None
        
        # Buscar preço atual
        current_price = BrapiService.get_current_price(ticker)
        if not current_price or current_price <= 0:
            return None
        
        # Somar dividendos do período
        dividends = BrapiService.get_dividends(ticker, range_days)
        total_dividends = sum(d["valor_por_acao"] for d in dividends)
        
        if total_dividends <= 0:
            return None
        
        # Calcular yield: (dividendos anuais / preço) * 100
        # Se range_days for 1y, já está anualizado
        # Se for outro período, precisamos anualizar
        if range_days == "1y":
            yield_value = (total_dividends / current_price) * Decimal("100")
        else:
            # Aproximação: assumir que o período representa proporção do ano
            # Para simplificar, vamos usar apenas 1y
            yield_value = (total_dividends / current_price) * Decimal("100")
        
        return yield_value.quantize(Decimal("0.01"))
    
    @staticmethod
    def get_company_info(ticker: str) -> Optional[Dict]:
        """
        Busca informações da empresa.
        
        Args:
            ticker: Código do ativo
        
        Returns:
            Dict com informações da empresa ou None
        """
        quote_data = BrapiService.get_quote(ticker, range_days="1d", dividends=False)
        
        if not quote_data:
            return None
        
        return {
            "nome": quote_data.get("longName") or quote_data.get("shortName", ""),
            "setor": quote_data.get("sector", ""),
            "pais": "Brasil",  # Brapi é focado em B3
        }

