# Integração com API Brapi

## O que foi implementado

### Backend (Django)

1. **Novo serviço: `brapi_service.py`**
   - Classe `BrapiService` para consumir a API Brapi (brapi.dev)
   - Métodos disponíveis:
     - `get_quote()`: Busca informações gerais de uma ação
     - `get_dividends()`: Extrai e formata dividendos
     - `get_current_price()`: Busca preço atual
     - `calculate_yield()`: Calcula dividend yield
     - `get_company_info()`: Busca informações da empresa

2. **Novos endpoints na API:**
   - `POST /api/ativos/buscar_dados_brapi/` - Busca dados de uma ação na Brapi
   - `POST /api/ativos/{id}/importar_dividendos_brapi/` - Importa dividendos de um ativo

3. **Melhorias na simulação:**
   - Agora tenta buscar yield real da Brapi antes de usar valor padrão
   - Calcula yield baseado em preços e dividendos reais

### Frontend (React)

1. **Página de Ativos atualizada:**
   - Botão "🔍 Buscar na Brapi" para buscar dados reais
   - Formulário de busca com preview dos dados
   - Botão para criar ativo automaticamente com dados da Brapi
   - Botão "📥 Importar Dividendos" em cada ativo para importar histórico

2. **Novos métodos na API service:**
   - `buscarDadosBrapi(ticker)`
   - `importarDividendosBrapi(id)`

## Como usar

### 1. Buscar e criar ativo da Brapi

1. Acesse a página "Ativos"
2. Clique em "🔍 Buscar na Brapi"
3. Digite o ticker (ex: PETR4, VALE3)
4. Clique em "Buscar"
5. Revise os dados encontrados
6. Clique em "Criar Ativo com Estes Dados"

### 2. Importar dividendos

1. Na lista de ativos, clique em "📥 Importar Dividendos" no ativo desejado
2. Os dividendos do último ano serão importados automaticamente
3. Duplicatas são ignoradas automaticamente

### 3. Simulação com dados reais

- Ao executar uma simulação, o sistema tenta buscar yields reais da Brapi
- Se não conseguir, usa os dividendos locais para calcular
- Se não houver dados, usa yield padrão de 6%

## Exemplo de uso da API Brapi

```python
from planner.brapi_service import BrapiService

# Buscar dados de uma ação
dados = BrapiService.get_quote("PETR4", range_days="1y", dividends=True)

# Buscar dividendos
dividendos = BrapiService.get_dividends("PETR4", range_days="1y")

# Calcular yield
yield_value = BrapiService.calculate_yield("PETR4", range_days="1y")

# Preço atual
preco = BrapiService.get_current_price("PETR4")
```

## Limitações da API Brapi

- Plano gratuito tem limite de requisições diárias
- Dados são apenas para ações brasileiras (B3)
- Histórico de dividendos pode ser limitado

## Documentação da Brapi

- Site: https://brapi.dev
- Documentação: https://brapi.dev/docs
- Endpoint usado: `GET https://brapi.dev/api/quote/{ticker}?range=1y&dividends=true`

