import React, { useState, useEffect } from 'react'
import { ativosAPI } from '../services/api'
import AtivoForm from '../components/AtivoForm'
import './AtivosPage.css'

function AtivosPage() {
  const [ativos, setAtivos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingAtivo, setEditingAtivo] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [showBrapiSearch, setShowBrapiSearch] = useState(false)
  const [brapiTicker, setBrapiTicker] = useState('')
  const [brapiData, setBrapiData] = useState(null)
  const [loadingBrapi, setLoadingBrapi] = useState(false)

  useEffect(() => {
    carregarAtivos()
  }, [searchTerm])

  const carregarAtivos = async () => {
    try {
      setLoading(true)
      const response = await ativosAPI.listar(searchTerm)
      setAtivos(response.data.results || response.data)
      setError(null)
    } catch (err) {
      setError('Erro ao carregar ativos. Certifique-se de que o backend está rodando.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (dados) => {
    try {
      // Por enquanto, usar usuário padrão (id=1)
      // Em produção, isso viria da autenticação
      await ativosAPI.criar({ ...dados, usuario: 1 })
      setShowForm(false)
      carregarAtivos()
    } catch (err) {
      alert('Erro ao criar ativo: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleUpdate = async (id, dados) => {
    try {
      await ativosAPI.atualizar(id, { ...dados, usuario: 1 })
      setEditingAtivo(null)
      carregarAtivos()
    } catch (err) {
      alert('Erro ao atualizar ativo: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este ativo?')) {
      return
    }
    try {
      await ativosAPI.deletar(id)
      carregarAtivos()
    } catch (err) {
      alert('Erro ao excluir ativo: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleEdit = (ativo) => {
    setEditingAtivo(ativo)
    setShowForm(true)
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingAtivo(null)
  }

  const handleBuscarBrapi = async () => {
    if (!brapiTicker.trim()) {
      alert('Digite um ticker para buscar')
      return
    }

    try {
      setLoadingBrapi(true)
      setError(null)
      const response = await ativosAPI.buscarDadosBrapi(brapiTicker.toUpperCase())
      
      // Verificar se há erro na resposta
      if (response.data.erro) {
        setError(response.data.erro)
        setBrapiData(null)
        return
      }
      
      setBrapiData(response.data)
    } catch (err) {
      console.error('Erro completo ao buscar na Brapi:', err)
      console.error('Response:', err.response)
      console.error('Response data:', err.response?.data)
      
      let errorMsg = 'Erro desconhecido'
      
      if (err.response) {
        // Erro com resposta do servidor
        if (err.response.data) {
          errorMsg = err.response.data.erro || err.response.data.detail || err.response.data.message || `Erro ${err.response.status}`
        } else {
          errorMsg = `Erro ${err.response.status}: ${err.response.statusText || 'Erro no servidor'}`
        }
      } else if (err.request) {
        // Requisição foi feita mas não houve resposta
        errorMsg = 'Sem resposta do servidor. Verifique se o backend está rodando em http://localhost:8000'
      } else {
        // Erro ao configurar a requisição
        errorMsg = err.message || 'Erro ao fazer requisição'
      }
      
      setError(`Erro ao buscar dados da Brapi: ${errorMsg}`)
      setBrapiData(null)
    } finally {
      setLoadingBrapi(false)
    }
  }

  const handleCriarComDadosBrapi = async () => {
    if (!brapiData) return

    try {
      await ativosAPI.criar({
        ticker: brapiData.ticker,
        nome_empresa: brapiData.nome_empresa || brapiData.ticker,
        setor: brapiData.setor || '',
        pais: brapiData.pais || 'Brasil',
        usuario: 1
      })
      setShowBrapiSearch(false)
      setBrapiData(null)
      setBrapiTicker('')
      carregarAtivos()
      alert('Ativo criado com sucesso! Agora você pode importar os dividendos.')
    } catch (err) {
      alert('Erro ao criar ativo: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleImportarDividendos = async (ativoId) => {
    if (!window.confirm('Deseja importar dividendos da Brapi para este ativo?')) {
      return
    }

    try {
      const response = await ativosAPI.importarDividendosBrapi(ativoId)
      alert(`Importação concluída!\n${response.data.importados} novos registros importados\n${response.data.duplicados} duplicados ignorados`)
      carregarAtivos()
    } catch (err) {
      alert('Erro ao importar dividendos: ' + (err.response?.data?.erro || err.message))
    }
  }

  if (loading && ativos.length === 0) {
    return <div className="loading">Carregando ativos...</div>
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header d-flex justify-content-between">
          <h2>Gerenciar Ativos</h2>
          <div className="d-flex gap-2">
            <button
              className="btn btn-secondary"
              onClick={() => {
                setShowBrapiSearch(!showBrapiSearch)
                setShowForm(false)
              }}
            >
              {showBrapiSearch ? 'Cancelar' : '🔍 Buscar na Brapi'}
            </button>
            <button
              className="btn btn-primary"
              onClick={() => {
                setEditingAtivo(null)
                setShowForm(!showForm)
                setShowBrapiSearch(false)
              }}
            >
              {showForm ? 'Cancelar' : '+ Novo Ativo'}
            </button>
          </div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {showBrapiSearch && (
          <div className="brapi-search-box" style={{ marginBottom: '1.5rem', padding: '2rem', background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', border: '1px solid rgba(226, 232, 240, 0.8)', boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)' }}>
            <h3 style={{ color: 'var(--primary-color)', fontFamily: "'Playfair Display', serif", fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Buscar Ativo na Brapi</h3>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '1rem' }}>
              Busque dados reais de ações brasileiras na API Brapi (brapi.dev)
            </p>
            <div className="d-flex gap-2" style={{ marginBottom: '1rem' }}>
              <input
                type="text"
                className="form-control"
                placeholder="Digite o ticker (ex: PETR4, VALE3)"
                value={brapiTicker}
                onChange={(e) => setBrapiTicker(e.target.value.toUpperCase())}
                onKeyPress={(e) => e.key === 'Enter' && handleBuscarBrapi()}
                style={{ maxWidth: '300px' }}
              />
              <button
                className="btn btn-primary"
                onClick={handleBuscarBrapi}
                disabled={loadingBrapi}
              >
                {loadingBrapi ? 'Buscando...' : 'Buscar'}
              </button>
            </div>

            {brapiData && (
              <div className="brapi-results" style={{ marginTop: '1rem', padding: '1rem', background: 'white', borderRadius: '4px' }}>
                <h4>Dados Encontrados:</h4>
                <div style={{ marginTop: '0.5rem' }}>
                  <p><strong>Ticker:</strong> {brapiData.ticker}</p>
                  <p><strong>Nome:</strong> {brapiData.nome_empresa || 'N/A'}</p>
                  <p><strong>Setor:</strong> {brapiData.setor || 'N/A'}</p>
                  <p><strong>Preço Atual:</strong> {brapiData.preco_atual ? `R$ ${brapiData.preco_atual.toFixed(2)}` : 'N/A'}</p>
                  <p><strong>Yield Anual:</strong> {brapiData.yield_anual ? `${brapiData.yield_anual.toFixed(2)}%` : 'N/A'}</p>
                  <p><strong>Dividendos (último ano):</strong> {brapiData.total_dividendos_ano || 0} pagamentos</p>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={handleCriarComDadosBrapi}
                  style={{ marginTop: '1rem' }}
                >
                  Criar Ativo com Estes Dados
                </button>
              </div>
            )}
          </div>
        )}

        {showForm && (
          <AtivoForm
            ativo={editingAtivo}
            onSubmit={editingAtivo ? (dados) => handleUpdate(editingAtivo.id, dados) : handleCreate}
            onCancel={handleCancel}
          />
        )}

        <div className="search-box">
          <input
            type="text"
            className="form-control"
            placeholder="Buscar por ticker, nome ou setor..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {ativos.length === 0 ? (
          <p className="text-center mt-3">Nenhum ativo cadastrado ainda.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Nome da Empresa</th>
                <th>Setor</th>
                <th>País</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {ativos.map((ativo) => (
                <tr key={ativo.id}>
                  <td><strong>{ativo.ticker}</strong></td>
                  <td>{ativo.nome_empresa}</td>
                  <td>{ativo.setor || '-'}</td>
                  <td>{ativo.pais}</td>
                  <td>
                    <div className="d-flex gap-1">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(ativo)}
                        title="Editar ativo"
                      >
                        Editar
                      </button>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleImportarDividendos(ativo.id)}
                        title="Importar dividendos da Brapi"
                      >
                        📥 Importar Dividendos
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(ativo.id)}
                        title="Excluir ativo"
                      >
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default AtivosPage

