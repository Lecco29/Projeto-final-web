import React, { useState, useEffect } from 'react'

function MetaRendaForm({ meta, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    nome: '',
    renda_mensal_desejada: '',
    anos_para_atingir: '',
    inflacao_media_anual: '4.5',
    percentual_reinvestimento: '0',
  })

  useEffect(() => {
    if (meta) {
      setFormData({
        nome: meta.nome || '',
        renda_mensal_desejada: meta.renda_mensal_desejada || '',
        anos_para_atingir: meta.anos_para_atingir || '',
        inflacao_media_anual: meta.inflacao_media_anual || '4.5',
        percentual_reinvestimento: meta.percentual_reinvestimento || '0',
      })
    }
  }, [meta])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validações
    if (!formData.nome.trim()) {
      alert('O nome da meta é obrigatório')
      return
    }
    if (!formData.renda_mensal_desejada || parseFloat(formData.renda_mensal_desejada) <= 0) {
      alert('A renda mensal desejada deve ser maior que zero')
      return
    }
    if (!formData.anos_para_atingir || parseInt(formData.anos_para_atingir) < 1) {
      alert('Deve ter pelo menos 1 ano para atingir a meta')
      return
    }

    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="meta-renda-form">
      <div className="form-group">
        <label className="form-label" htmlFor="nome">
          Nome da Meta *
        </label>
        <input
          type="text"
          id="nome"
          name="nome"
          className="form-control"
          value={formData.nome}
          onChange={handleChange}
          placeholder="Ex: Independência Financeira"
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="renda_mensal_desejada">
          Renda Mensal Desejada (R$) *
        </label>
        <input
          type="number"
          id="renda_mensal_desejada"
          name="renda_mensal_desejada"
          className="form-control"
          value={formData.renda_mensal_desejada}
          onChange={handleChange}
          step="0.01"
          min="0"
          placeholder="0.00"
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="anos_para_atingir">
          Anos para Atingir *
        </label>
        <input
          type="number"
          id="anos_para_atingir"
          name="anos_para_atingir"
          className="form-control"
          value={formData.anos_para_atingir}
          onChange={handleChange}
          min="1"
          placeholder="Ex: 10"
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="inflacao_media_anual">
          Inflação Média Anual (%)
        </label>
        <input
          type="number"
          id="inflacao_media_anual"
          name="inflacao_media_anual"
          className="form-control"
          value={formData.inflacao_media_anual}
          onChange={handleChange}
          step="0.01"
          min="0"
          max="100"
          placeholder="4.5"
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="percentual_reinvestimento">
          Percentual de Reinvestimento (%)
        </label>
        <input
          type="number"
          id="percentual_reinvestimento"
          name="percentual_reinvestimento"
          className="form-control"
          value={formData.percentual_reinvestimento}
          onChange={handleChange}
          step="0.01"
          min="0"
          max="100"
          placeholder="0"
        />
        <small style={{ color: '#666', fontSize: '0.875rem' }}>
          Percentual dos dividendos que serão reinvestidos automaticamente
        </small>
      </div>

      <div className="form-actions d-flex gap-2">
        <button type="submit" className="btn btn-primary">
          {meta ? 'Atualizar' : 'Criar'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default MetaRendaForm

