import React, { useState, useEffect } from 'react'
import { historicoDividendosAPI, ativosAPI } from '../services/api'
import HistoricoDividendoForm from '../components/HistoricoDividendoForm'
import './HistoricoDividendosPage.css'

function HistoricoDividendosPage() {
  const [historico, setHistorico] = useState([])
  const [ativos, setAtivos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [filtros, setFiltros] = useState({
    ativo: '',
    data_inicio: '',
    data_fim: '',
  })

  useEffect(() => {
    carregarAtivos()
    carregarHistorico()
  }, [filtros])

  const carregarAtivos = async () => {
    try {
      const response = await ativosAPI.listar()
      setAtivos(response.data.results || response.data)
    } catch (err) {
      console.error('Erro ao carregar ativos:', err)
    }
  }

  const carregarHistorico = async () => {
    try {
      setLoading(true)
      const response = await historicoDividendosAPI.listar(filtros)
      setHistorico(response.data.results || response.data)
      setError(null)
    } catch (err) {
      setError('Erro ao carregar histórico. Certifique-se de que o backend está rodando.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (dados) => {
    try {
      await historicoDividendosAPI.criar(dados)
      setShowForm(false)
      carregarHistorico()
    } catch (err) {
      alert('Erro ao criar registro: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleUpdate = async (id, dados) => {
    try {
      await historicoDividendosAPI.atualizar(id, dados)
      setEditingItem(null)
      carregarHistorico()
    } catch (err) {
      alert('Erro ao atualizar registro: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este registro?')) {
      return
    }
    try {
      await historicoDividendosAPI.deletar(id)
      carregarHistorico()
    } catch (err) {
      alert('Erro ao excluir registro: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleEdit = (item) => {
    setEditingItem(item)
    setShowForm(true)
  }

  const handleFiltroChange = (e) => {
    const { name, value } = e.target
    setFiltros((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const formatarData = (data) => {
    if (!data) return '-'
    const date = new Date(data)
    return date.toLocaleDateString('pt-BR')
  }

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor)
  }

  if (loading && historico.length === 0) {
    return <div className="loading">Carregando histórico...</div>
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header d-flex justify-content-between">
          <h2>Histórico de Dividendos</h2>
          <button
            className="btn btn-primary"
            onClick={() => {
              setEditingItem(null)
              setShowForm(!showForm)
            }}
          >
            {showForm ? 'Cancelar' : '+ Novo Registro'}
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {showForm && (
          <HistoricoDividendoForm
            item={editingItem}
            ativos={ativos}
            onSubmit={editingItem ? (dados) => handleUpdate(editingItem.id, dados) : handleCreate}
            onCancel={() => {
              setShowForm(false)
              setEditingItem(null)
            }}
          />
        )}

        <div className="filtros-box">
          <h3>Filtros</h3>
          <div className="filtros-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="filtro_ativo">
                Ativo
              </label>
              <select
                id="filtro_ativo"
                name="ativo"
                className="form-control"
                value={filtros.ativo}
                onChange={handleFiltroChange}
              >
                <option value="">Todos</option>
                {ativos.map((ativo) => (
                  <option key={ativo.id} value={ativo.id}>
                    {ativo.ticker} - {ativo.nome_empresa}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="filtro_data_inicio">
                Data Início
              </label>
              <input
                type="date"
                id="filtro_data_inicio"
                name="data_inicio"
                className="form-control"
                value={filtros.data_inicio}
                onChange={handleFiltroChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="filtro_data_fim">
                Data Fim
              </label>
              <input
                type="date"
                id="filtro_data_fim"
                name="data_fim"
                className="form-control"
                value={filtros.data_fim}
                onChange={handleFiltroChange}
              />
            </div>
          </div>
        </div>

        {historico.length === 0 ? (
          <p className="text-center mt-3">Nenhum registro de dividendo encontrado.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Ativo</th>
                <th>Data de Pagamento</th>
                <th>Valor por Ação</th>
                <th>Fonte</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {historico.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>{item.ativo_ticker || item.ativo}</strong>
                    {item.ativo_nome && <div style={{ fontSize: '0.875rem', color: '#666' }}>{item.ativo_nome}</div>}
                  </td>
                  <td>{formatarData(item.data_pagamento)}</td>
                  <td>{formatarMoeda(item.valor_por_acao)}</td>
                  <td>{item.fonte === 'manual' ? 'Manual' : 'API'}</td>
                  <td>
                    <div className="d-flex gap-1">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(item)}
                      >
                        Editar
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(item.id)}
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

export default HistoricoDividendosPage

