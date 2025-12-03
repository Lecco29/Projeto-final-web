"""
Serviço para consumir a API Brapi (brapi.dev) e buscar dados de ações brasileiras.
"""

import requests
import os
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta


# Classe para interagir com a API Brapi. Alguns tickers são gratuitos (PETR4, MGLU3, VALE3, ITUB4), para outros é necessário token.
class BrapiService:
    
    BASE_URL = "https://brapi.dev/api"
    
    # Tickers gratuitos que não precisam de token
    FREE_TICKERS = ["PETR4", "MGLU3", "VALE3", "ITUB4"]
    
    # Testa se a conexão com a Brapi está funcionando.
    @staticmethod
    def test_connection() -> bool:
        try:
            response = requests.get("https://brapi.dev/api/quote/PETR4", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    # Busca informações de uma ação, incluindo preço e dividendos.
    @staticmethod
    def get_quote(ticker: str, range_days: str = "1y", dividends: bool = True) -> Optional[Dict]:
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
                    dados_erro = response.json()
                    msg = dados_erro.get("error") or dados_erro.get("message", f"Erro HTTP {response.status_code}")
                    print(f"Detalhes: {msg}")
                except:
                    print(f"Resposta: {response.text[:200]}")
                return None
            
            # Verificar se há erro na resposta JSON
            try:
                dados = response.json()
                
                # Verificar se há mensagem de erro
                if "error" in dados or "message" in dados:
                    msg = dados.get("error") or dados.get("message", "Erro desconhecido")
                    print(f"Erro da API Brapi para {ticker}: {msg}")
                    return None
                
                # A API retorna um array de resultados
                if "results" in dados and len(dados["results"]) > 0:
                    return dados["results"][0]
                
                # Se não tem results, pode ser que retornou diretamente
                if isinstance(dados, dict) and "symbol" in dados:
                    return dados
                
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
    
    # Extrai e formata os dividendos de uma ação.
    @staticmethod
    def get_dividends(ticker: str, range_days: str = "1y") -> List[Dict]:
        dados = BrapiService.get_quote(ticker, range_days, dividends=True)
        
        if not dados:
            return []
        
        dividendos = []
        
        # A API retorna dividendos no formato:
        # "dividendsData": {
        #   "cashDividends": [{"paymentDate": "2024-01-15T00:00:00.000Z", "rate": 0.50}, ...],
        #   "stockDividends": [...],
        #   "subscriptions": [...]
        # }
        if "dividendsData" in dados:
            info_dividendos = dados["dividendsData"]
            
            # Novo formato: dividendsData é um objeto com cashDividends
            if isinstance(info_dividendos, dict):
                dividendos_dinheiro = info_dividendos.get("cashDividends", [])
                
                for div in dividendos_dinheiro:
                    try:
                        if not isinstance(div, dict):
                            continue
                        
                        # Extrair data de pagamento
                        data = div.get("paymentDate", "")
                        if data:
                            # Converter de ISO 8601 para formato YYYY-MM-DD
                            if isinstance(data, str):
                                # Remover timezone e pegar apenas a data
                                data_str = data.split('T')[0] if 'T' in data else data
                            else:
                                data_str = str(data)
                        else:
                            continue
                        
                        # Extrair valor do dividendo (rate)
                        valor = div.get("rate", 0)
                        
                        # Converter para Decimal
                        if isinstance(valor, (int, float)):
                            valor = Decimal(str(valor))
                        else:
                            valor = Decimal(str(valor)) if valor else Decimal('0')
                        
                        if data_str and valor > 0:
                            dividendos.append({
                                "data_pagamento": data_str,
                                "valor_por_acao": valor,
                                "fonte": "api"
                            })
                    except Exception as e:
                        print(f"Erro ao processar dividendo: {e}")
                        continue
            
            # Formato antigo (compatibilidade): dividendsData é uma lista direta
            elif isinstance(info_dividendos, list):
                for div in info_dividendos:
                    try:
                        if not isinstance(div, dict):
                            continue
                        
                        data_str = div.get("date", "")
                        valor = div.get("dividend", 0)
                        
                        if isinstance(valor, (int, float)):
                            valor = Decimal(str(valor))
                        else:
                            valor = Decimal(str(valor)) if valor else Decimal('0')
                        
                        if data_str and valor > 0:
                            dividendos.append({
                                "data_pagamento": data_str,
                                "valor_por_acao": valor,
                                "fonte": "api"
                            })
                    except Exception as e:
                        print(f"Erro ao processar dividendo: {e}")
                        continue
        
        return dividendos
    
    # Busca o preço atual de uma ação.
    @staticmethod
    def get_current_price(ticker: str) -> Optional[Decimal]:
        dados = BrapiService.get_quote(ticker, range_days="1d", dividends=False)
        
        if not dados:
            return None
        
        # A API retorna o preço em "regularMarketPrice" ou "price"
        preco = dados.get("regularMarketPrice") or dados.get("price")
        
        if preco:
            try:
                return Decimal(str(preco))
            except:
                return None
        
        return None
    
    # Calcula o yield (dividend yield) de uma ação baseado nos dividendos do último ano.
    @staticmethod
    def calculate_yield(ticker: str, range_days: str = "1y") -> Optional[Decimal]:
        dados = BrapiService.get_quote(ticker, range_days, dividends=True)
        
        if not dados:
            return None
        
        # Buscar preço atual
        preco = BrapiService.get_current_price(ticker)
        if not preco or preco <= 0:
            return None
        
        # Somar dividendos do período
        dividendos = BrapiService.get_dividends(ticker, range_days)
        total = sum(d["valor_por_acao"] for d in dividendos)
        
        if total <= 0:
            return None
        
        # Calcular yield: (dividendos anuais / preço) * 100
        # Se range_days for 1y, já está anualizado
        # Se for outro período, precisamos anualizar
        if range_days == "1y":
            yield_calc = (total / preco) * Decimal("100")
        else:
            # Aproximação: assumir que o período representa proporção do ano
            # Para simplificar, vamos usar apenas 1y
            yield_calc = (total / preco) * Decimal("100")
        
        return yield_calc.quantize(Decimal("0.01"))
    
    # Busca informações da empresa.
    @staticmethod
    def get_company_info(ticker: str) -> Optional[Dict]:
        dados = BrapiService.get_quote(ticker, range_days="1d", dividends=False)
        
        if not dados:
            return None
        
        return {
            "nome": dados.get("longName") or dados.get("shortName", ""),
            "setor": dados.get("sector", ""),
            "pais": "Brasil",  # Brapi é focado em B3
        }

