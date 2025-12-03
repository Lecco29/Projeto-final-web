import React, { useState, useEffect } from 'react'
import { ativosAPI } from '../services/api'

function AtivoForm({ ativo, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    ticker: '',
    nome_empresa: '',
    setor: '',
    pais: 'Brasil',
    observacoes: '',
  })
  const [loadingBrapi, setLoadingBrapi] = useState(false)
  const debounceTimerRef = React.useRef(null)

  useEffect(() => {
    if (ativo) {
      setFormData({
        ticker: ativo.ticker || '',
        nome_empresa: ativo.nome_empresa || '',
        setor: ativo.setor || '',
        pais: ativo.pais || 'Brasil',
        observacoes: ativo.observacoes || '',
      })
    }
  }, [ativo])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    
    // Se mudou o ticker e não está editando, buscar dados da Brapi com debounce
    if (name === 'ticker' && !ativo && value.length >= 4) {
      // Limpar timer anterior
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
      
      // Aguardar 800ms antes de buscar
      debounceTimerRef.current = setTimeout(() => {
        buscarDadosBrapi(value.toUpperCase())
      }, 800)
    }
  }

  const buscarDadosBrapi = async (ticker) => {
    if (!ticker || ticker.length < 4) return
    
    try {
      setLoadingBrapi(true)
      const response = await ativosAPI.buscarDadosBrapi(ticker)
      const dados = response.data
      
      // Verificar se há erro na resposta
      if (dados.erro) {
        console.warn('Erro da Brapi:', dados.erro)
        return
      }
      
      if (dados) {
        setFormData(prev => ({
          ...prev,
          nome_empresa: dados.nome_empresa || prev.nome_empresa,
          setor: dados.setor || prev.setor,
          pais: dados.pais || prev.pais,
        }))
      }
    } catch (err) {
      // Silenciosamente falha - não é obrigatório ter dados da Brapi
      console.warn('Não foi possível buscar dados da Brapi para', ticker, err.message)
      // Não mostrar erro para o usuário, pois é opcional
    } finally {
      setLoadingBrapi(false)
    }
  }

  // Limpar timer ao desmontar
  React.useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validações básicas
    if (!formData.ticker.trim()) {
      alert('O ticker é obrigatório')
      return
    }
    if (!formData.nome_empresa.trim()) {
      alert('O nome da empresa é obrigatório')
      return
    }

    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="ativo-form">
      <div className="form-group">
        <label className="form-label" htmlFor="ticker">
          Ticker *
        </label>
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            id="ticker"
            name="ticker"
            className="form-control"
            value={formData.ticker}
            onChange={handleChange}
            placeholder="Ex: PETR4, VALE3"
            required
            style={{ textTransform: 'uppercase' }}
          />
          {loadingBrapi && (
            <span style={{ 
              position: 'absolute', 
              right: '10px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              fontSize: '0.875rem',
              color: 'var(--accent-color)'
            }}>
              Buscando...
            </span>
          )}
        </div>
        {!ativo && formData.ticker.length >= 4 && (
          <small style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Dados serão buscados automaticamente da Brapi ao digitar o ticker
          </small>
        )}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="nome_empresa">
          Nome da Empresa *
        </label>
        <input
          type="text"
          id="nome_empresa"
          name="nome_empresa"
          className="form-control"
          value={formData.nome_empresa}
          onChange={handleChange}
          placeholder="Nome completo da empresa"
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="setor">
          Setor
        </label>
        <input
          type="text"
          id="setor"
          name="setor"
          className="form-control"
          value={formData.setor}
          onChange={handleChange}
          placeholder="Ex: Petróleo, Mineração"
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="pais">
          País
        </label>
        <input
          type="text"
          id="pais"
          name="pais"
          className="form-control"
          value={formData.pais}
          onChange={handleChange}
          placeholder="País de origem"
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="observacoes">
          Observações
        </label>
        <textarea
          id="observacoes"
          name="observacoes"
          className="form-control"
          value={formData.observacoes}
          onChange={handleChange}
          rows="3"
          placeholder="Observações adicionais sobre o ativo"
        />
      </div>

      <div className="form-actions d-flex gap-2">
        <button type="submit" className="btn btn-primary">
          {ativo ? 'Atualizar' : 'Criar'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default AtivoForm

