import React, { useState, useEffect } from 'react'
import { metasRendaAPI } from '../services/api'
import MetaRendaForm from '../components/MetaRendaForm'
import './MetasRendaPage.css'

function MetasRendaPage() {
  const [metas, setMetas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingMeta, setEditingMeta] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    carregarMetas()
  }, [searchTerm])

  const carregarMetas = async () => {
    try {
      setLoading(true)
      const response = await metasRendaAPI.listar(searchTerm)
      setMetas(response.data.results || response.data)
      setError(null)
    } catch (err) {
      setError('Erro ao carregar metas. Certifique-se de que o backend está rodando.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (dados) => {
    try {
      await metasRendaAPI.criar({ ...dados, usuario: 1 })
      setShowForm(false)
      carregarMetas()
    } catch (err) {
      alert('Erro ao criar meta: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleUpdate = async (id, dados) => {
    try {
      await metasRendaAPI.atualizar(id, { ...dados, usuario: 1 })
      setEditingMeta(null)
      carregarMetas()
    } catch (err) {
      alert('Erro ao atualizar meta: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir esta meta?')) {
      return
    }
    try {
      await metasRendaAPI.deletar(id)
      carregarMetas()
    } catch (err) {
      alert('Erro ao excluir meta: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleEdit = (meta) => {
    setEditingMeta(meta)
    setShowForm(true)
  }

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor)
  }

  if (loading && metas.length === 0) {
    return <div className="loading">Carregando metas...</div>
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header d-flex justify-content-between">
          <h2>Metas de Renda</h2>
          <button
            className="btn btn-primary"
            onClick={() => {
              setEditingMeta(null)
              setShowForm(!showForm)
            }}
          >
            {showForm ? 'Cancelar' : '+ Nova Meta'}
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {showForm && (
          <MetaRendaForm
            meta={editingMeta}
            onSubmit={editingMeta ? (dados) => handleUpdate(editingMeta.id, dados) : handleCreate}
            onCancel={() => {
              setShowForm(false)
              setEditingMeta(null)
            }}
          />
        )}

        <div className="search-box">
          <input
            type="text"
            className="form-control"
            placeholder="Buscar por nome ou valor de renda..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {metas.length === 0 ? (
          <p className="text-center mt-3">Nenhuma meta cadastrada ainda.</p>
        ) : (
          <div className="metas-grid">
            {metas.map((meta) => (
              <div key={meta.id} className="meta-card">
                <h3>{meta.nome}</h3>
                <div className="meta-info">
                  <div className="meta-item">
                    <strong>Renda Mensal Desejada:</strong>
                    <span>{formatarMoeda(meta.renda_mensal_desejada)}</span>
                  </div>
                  <div className="meta-item">
                    <strong>Anos para Atingir:</strong>
                    <span>{meta.anos_para_atingir} anos</span>
                  </div>
                  <div className="meta-item">
                    <strong>Inflação Média Anual:</strong>
                    <span>{meta.inflacao_media_anual}%</span>
                  </div>
                  <div className="meta-item">
                    <strong>Reinvestimento:</strong>
                    <span>{meta.percentual_reinvestimento}%</span>
                  </div>
                </div>
                <div className="meta-actions d-flex gap-1">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleEdit(meta)}
                  >
                    Editar
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(meta.id)}
                  >
                    Excluir
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MetasRendaPage

