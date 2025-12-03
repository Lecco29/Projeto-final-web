/**
 * Serviço de API para comunicação com o backend Django.
 * Configuração do axios e funções para todas as operações CRUD.
 */

import axios from 'axios'

// Configurar base URL da API
// Usar URL direta do backend (CORS já está configurado)
const API_BASE_URL = 'http://localhost:8000/api'

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar autenticação (se necessário no futuro)
api.interceptors.request.use(
  (config) => {
    // Aqui pode adicionar token de autenticação se necessário
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Melhorar mensagens de erro
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      error.message = 'Erro de conexão. Verifique se o backend está rodando e sua conexão com a internet.'
    }
    return Promise.reject(error)
  }
)

// ========== ATIVOS ==========
export const ativosAPI = {
  listar: (search = '') => {
    const params = search ? { search } : {}
    return api.get('/ativos/', { params })
  },
  obter: (id) => api.get(`/ativos/${id}/`),
  criar: (dados) => api.post('/ativos/', dados),
  atualizar: (id, dados) => api.put(`/ativos/${id}/`, dados),
  deletar: (id) => api.delete(`/ativos/${id}/`),
  buscarDadosBrapi: (ticker) => api.post('/ativos/buscar_dados_brapi/', { ticker }),
  importarDividendosBrapi: (id) => api.post(`/ativos/${id}/importar_dividendos_brapi/`),
}

// ========== HISTÓRICO DE DIVIDENDOS ==========
export const historicoDividendosAPI = {
  listar: (filtros = {}) => {
    const params = {}
    if (filtros.ativo) params.ativo = filtros.ativo
    if (filtros.data_inicio) params.data_inicio = filtros.data_inicio
    if (filtros.data_fim) params.data_fim = filtros.data_fim
    return api.get('/historico-dividendos/', { params })
  },
  obter: (id) => api.get(`/historico-dividendos/${id}/`),
  criar: (dados) => api.post('/historico-dividendos/', dados),
  atualizar: (id, dados) => api.put(`/historico-dividendos/${id}/`, dados),
  deletar: (id) => api.delete(`/historico-dividendos/${id}/`),
}

// ========== METAS DE RENDA ==========
export const metasRendaAPI = {
  listar: (search = '') => {
    const params = search ? { search } : {}
    return api.get('/metas-renda/', { params })
  },
  obter: (id) => api.get(`/metas-renda/${id}/`),
  criar: (dados) => api.post('/metas-renda/', dados),
  atualizar: (id, dados) => api.put(`/metas-renda/${id}/`, dados),
  deletar: (id) => api.delete(`/metas-renda/${id}/`),
  simular: (id, dados) => api.post(`/metas-renda/${id}/simular/`, dados),
}

// ========== SIMULAÇÕES ==========
export const simulacoesAPI = {
  listar: (filtros = {}) => {
    const params = {}
    if (filtros.meta) params.meta = filtros.meta
    return api.get('/simulacoes/', { params })
  },
  obter: (id) => api.get(`/simulacoes/${id}/`),
  deletar: (id) => api.delete(`/simulacoes/${id}/`),
}

export default api

