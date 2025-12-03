import React, { useState, useEffect } from 'react'

function HistoricoDividendoForm({ item, ativos, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    ativo: '',
    data_pagamento: '',
    valor_por_acao: '',
    fonte: 'manual',
    observacoes: '',
  })

  useEffect(() => {
    if (item) {
      setFormData({
        ativo: item.ativo || '',
        data_pagamento: item.data_pagamento || '',
        valor_por_acao: item.valor_por_acao || '',
        fonte: item.fonte || 'manual',
        observacoes: item.observacoes || '',
      })
    }
  }, [item])

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
    if (!formData.ativo) {
      alert('Selecione um ativo')
      return
    }
    if (!formData.data_pagamento) {
      alert('A data de pagamento é obrigatória')
      return
    }
    if (!formData.valor_por_acao || parseFloat(formData.valor_por_acao) <= 0) {
      alert('O valor por ação deve ser maior que zero')
      return
    }

    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="historico-dividendo-form">
      <div className="form-group">
        <label className="form-label" htmlFor="ativo">
          Ativo *
        </label>
        <select
          id="ativo"
          name="ativo"
          className="form-control"
          value={formData.ativo}
          onChange={handleChange}
          required
        >
          <option value="">Selecione um ativo</option>
          {ativos.map((ativo) => (
            <option key={ativo.id} value={ativo.id}>
              {ativo.ticker} - {ativo.nome_empresa}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="data_pagamento">
          Data de Pagamento *
        </label>
        <input
          type="date"
          id="data_pagamento"
          name="data_pagamento"
          className="form-control"
          value={formData.data_pagamento}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="valor_por_acao">
          Valor por Ação (R$) *
        </label>
        <input
          type="number"
          id="valor_por_acao"
          name="valor_por_acao"
          className="form-control"
          value={formData.valor_por_acao}
          onChange={handleChange}
          step="0.0001"
          min="0"
          placeholder="0.0000"
          required
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="fonte">
          Fonte
        </label>
        <select
          id="fonte"
          name="fonte"
          className="form-control"
          value={formData.fonte}
          onChange={handleChange}
        >
          <option value="manual">Manual</option>
          <option value="api">API</option>
        </select>
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
          placeholder="Observações sobre este pagamento"
        />
      </div>

      <div className="form-actions d-flex gap-2">
        <button type="submit" className="btn btn-primary">
          {item ? 'Atualizar' : 'Criar'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default HistoricoDividendoForm

