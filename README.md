# Planejador de Dividendos

Aplicação web para planejamento de independência financeira com foco em dividendos. Desenvolvida como trabalho final da disciplina "Projeto e Desenvolvimento de Sistemas Web" (UTFPR).

## 📋 Descrição

Esta aplicação ajuda o usuário a:
- Cadastrar ações/tickers
- Registrar ou importar histórico de dividendos
- Definir metas de renda mensal
- Simular quanto de patrimônio precisa acumular e quanto deve investir por mês, considerando inflação e percentual de reinvestimento
- Visualizar um plano ao longo do tempo

## 🛠️ Stack Tecnológica

### Backend
- **Python 3.8+**
- **Django 4.2.7**
- **Django REST Framework 3.14.0**
- **django-cors-headers** (para permitir requisições do React)

### Frontend
- **React 18.2**
- **Vite** (build tool)
- **React Router** (navegação)
- **Axios** (requisições HTTP)

## 📁 Estrutura do Projeto

```
.
├── backend/                 # Projeto Django
│   ├── dividendos_planner/  # Configurações do projeto
│   ├── planner/             # App principal
│   │   ├── models.py        # Modelos Django (Ativo, HistoricoDividendo, MetaRenda, Simulacao)
│   │   ├── views.py         # Views/API REST
│   │   ├── serializers.py   # Serializers do DRF
│   │   ├── forms.py         # Formulários Django (ModelForm)
│   │   ├── services.py      # Lógica de simulação
│   │   ├── urls.py          # URLs da API
│   │   └── admin.py         # Configuração do Django Admin
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/                # Aplicação React
    ├── src/
    │   ├── pages/           # Páginas principais
    │   │   ├── AtivosPage.jsx
    │   │   ├── HistoricoDividendosPage.jsx
    │   │   ├── MetasRendaPage.jsx
    │   │   └── SimulacaoPage.jsx
    │   ├── components/      # Componentes reutilizáveis
    │   │   ├── AtivoForm.jsx
    │   │   ├── HistoricoDividendoForm.jsx
    │   │   └── MetaRendaForm.jsx
    │   ├── services/         # Serviços de API
    │   │   └── api.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- Node.js 16 ou superior
- npm ou yarn

### ⚠️ Nota sobre Criação do Projeto

Este projeto já foi criado e está pronto para uso. Se você quiser criar um projeto similar do zero, use os comandos oficiais:

**Django:**
```bash
pip install django
django-admin startproject backend
cd backend
python manage.py startapp planner
```

**React (Vite):**
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

### Backend (Django)

1. **Navegue até a pasta do backend:**
   ```bash
   cd backend
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute as migrações:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crie um superusuário (opcional, para acessar o Django Admin):**
   ```bash
   python manage.py createsuperuser
   ```
   Siga as instruções para criar um usuário. Este usuário terá ID=1 e será usado automaticamente pela aplicação.

6. **Inicie o servidor Django:**
   ```bash
   python manage.py runserver
   ```
   O servidor estará rodando em `http://localhost:8000`

### Frontend (React)

1. **Abra um novo terminal e navegue até a pasta do frontend:**
   ```bash
   cd frontend
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   # ou
   yarn install
   ```

3. **Inicie o servidor de desenvolvimento:**
   ```bash
   npm run dev
   # ou
   yarn dev
   ```
   A aplicação estará rodando em `http://localhost:5173`

## 📚 Funcionalidades Implementadas

### ✅ CRUD Completo

Todas as entidades principais possuem operações de Criar, Listar, Atualizar e Remover:

- **Ativos**: Gerenciar ações/tickers
- **Histórico de Dividendos**: Registrar pagamentos de dividendos
- **Metas de Renda**: Definir metas de renda mensal
- **Simulações**: Visualizar resultados de simulações (criadas automaticamente)

### ✅ Busca e Filtros

- **Ativos**: Busca por ticker, nome da empresa ou setor
- **Histórico de Dividendos**: Filtro por ativo e intervalo de datas
- **Metas de Renda**: Busca por nome ou valor de renda

### ✅ Formulários Django

- `AtivoForm` (ModelForm) para criar/editar ativos
- `HistoricoDividendoForm` (ModelForm) para criar/editar histórico
- `MetaRendaForm` (ModelForm) para criar/editar metas

### ✅ API REST

Endpoints disponíveis em `http://localhost:8000/api/`:

- `GET/POST /api/ativos/` - Listar e criar ativos
- `GET/PUT/DELETE /api/ativos/{id}/` - Detalhes, atualizar e deletar ativo
- `GET/POST /api/historico-dividendos/` - Listar e criar registros
- `GET/PUT/DELETE /api/historico-dividendos/{id}/` - Detalhes, atualizar e deletar
- `GET/POST /api/metas-renda/` - Listar e criar metas
- `GET/PUT/DELETE /api/metas-renda/{id}/` - Detalhes, atualizar e deletar
- `POST /api/metas-renda/{id}/simular/` - Executar simulação
- `GET/DELETE /api/simulacoes/{id}/` - Listar e deletar simulações

### ✅ Simulação de Dividendos

A lógica de simulação calcula:
- **Patrimônio Alvo**: Valor total necessário para gerar a renda desejada
- **Aporte Mensal**: Valor que precisa investir mensalmente
- **Renda Mensal Ajustada**: Renda ajustada pela inflação no ano alvo
- Considera inflação média anual e percentual de reinvestimento

## 🗄️ Modelos Django

### Relacionamentos

- **Usuario** (User padrão do Django) → **Ativo** (um-para-muitos)
- **Ativo** → **HistoricoDividendo** (um-para-muitos)
- **Usuario** → **MetaRenda** (um-para-muitos)
- **MetaRenda** → **Simulacao** (um-para-muitos)

### Modelos

1. **Ativo**
   - ticker, nome_empresa, setor, país, observações
   - Relacionado com Usuario

2. **HistoricoDividendo**
   - data_pagamento, valor_por_acao, fonte (manual/API), observações
   - Relacionado com Ativo

3. **MetaRenda**
   - nome, renda_mensal_desejada, anos_para_atingir, inflacao_media_anual, percentual_reinvestimento
   - Relacionado com Usuario

4. **Simulacao**
   - patrimonio_alvo, aporte_mensal, yield_medio_usado, data_execucao
   - Relacionado com MetaRenda

## 🎨 Interface do Usuário

A aplicação possui uma interface moderna e responsiva com:

- **Navegação**: Menu superior com links para todas as seções
- **Páginas**:
  - **Ativos**: Lista, busca, criação e edição de ativos
  - **Histórico**: Lista, filtros, criação e edição de registros de dividendos
  - **Metas**: Lista, busca, criação e edição de metas de renda
  - **Simulação**: Interface para executar simulações e visualizar resultados

## 🔧 Configurações Importantes

### CORS

O backend está configurado para aceitar requisições do frontend React nas portas 5173 e 3000.

### Autenticação

Por padrão, a autenticação está desabilitada para facilitar testes. A aplicação usa automaticamente o usuário com ID=1. Para habilitar autenticação, descomente as linhas `permission_classes = [IsAuthenticated]` em `backend/planner/views.py`.

### 🔑 API Brapi - Integração com Dados de Ações

A aplicação integra com a API Brapi (https://brapi.dev) para buscar dados reais de ações brasileiras.

#### Tickers Gratuitos

Alguns tickers estão disponíveis gratuitamente sem necessidade de token:
- **PETR4** (Petrobras)
- **MGLU3** (Magazine Luiza)
- **VALE3** (Vale)
- **ITUB4** (Itaú)

#### Token de Autenticação (Opcional)

Para acessar outros tickers (como ABEV3, BBAS3, etc.), você precisa de um token gratuito da Brapi:

1. **Obter Token:**
   - Acesse https://brapi.dev
   - Crie uma conta gratuita
   - Obtenha seu token de API

2. **Configurar Token:**
   
   **Opção 1: Variável de Ambiente (Recomendado)**
   ```bash
   # Windows (PowerShell)
   $env:BRAPI_TOKEN="seu_token_aqui"
   
   # Linux/Mac
   export BRAPI_TOKEN="seu_token_aqui"
   ```
   
   **Opção 2: Arquivo .env**
   - Crie um arquivo `.env` na pasta `backend/`
   - Adicione: `BRAPI_TOKEN=seu_token_aqui`
   - Instale `python-decouple` (já está no requirements.txt)
   - O código já está configurado para ler automaticamente

3. **Reiniciar o Backend:**
   Após configurar o token, reinicie o servidor Django para que as mudanças tenham efeito.

#### Endpoints da Brapi

- `POST /api/ativos/buscar_dados_brapi/` - Busca dados de um ticker
- `POST /api/ativos/{id}/importar_dividendos_brapi/` - Importa histórico de dividendos

**Nota:** Se você tentar buscar um ticker que não está na lista gratuita sem token, receberá uma mensagem informando que é necessário um token.

## 📝 Notas para o Professor

### Requisitos Atendidos

✅ **Django com ORM**: Todos os modelos usam Django ORM  
✅ **Múltiplos modelos com relacionamentos**: 4 modelos com relacionamentos um-para-muitos  
✅ **CRUD completo**: Todas as entidades principais têm CRUD completo via API + React  
✅ **Busca**: Implementada para todas as entidades principais  
✅ **Formulários Django**: 3 ModelForms implementados (AtivoForm, HistoricoDividendoForm, MetaRendaForm)  
✅ **Problema real**: Sistema para planejamento de independência financeira  
✅ **Não é**: Sistema de gastos, lista de tarefas, biblioteca, oficina, fórum ou blog  

### Arquitetura

- **Backend**: Django REST Framework com ViewSets
- **Frontend**: React com componentes funcionais e hooks
- **Separação de responsabilidades**: Lógica de negócio em `services.py`, views apenas para API
- **Código comentado**: Principais funções e classes possuem documentação

## 🐛 Solução de Problemas

### Backend não inicia
- Verifique se o ambiente virtual está ativado
- Certifique-se de que todas as dependências foram instaladas
- Execute `python manage.py migrate` novamente

### Frontend não conecta com o backend
- Verifique se o backend está rodando em `http://localhost:8000`
- Verifique as configurações de CORS em `backend/dividendos_planner/settings.py`
- No navegador, abra o console (F12) para ver erros de CORS

### Erro ao criar registros
- Certifique-se de que existe um usuário com ID=1 no banco de dados
- Execute `python manage.py createsuperuser` para criar um usuário

## 📄 Licença

Este projeto foi desenvolvido como trabalho acadêmico.

## 👤 Autor

Desenvolvido como trabalho final da disciplina "Projeto e Desenvolvimento de Sistemas Web" - UTFPR.

