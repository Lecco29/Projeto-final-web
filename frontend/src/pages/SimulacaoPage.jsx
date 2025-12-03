import React, { useState, useEffect } from 'react'
import { metasRendaAPI, ativosAPI } from '../services/api'
import './SimulacaoPage.css'

function SimulacaoPage() {
  const [metas, setMetas] = useState([])
  const [ativos, setAtivos] = useState([])
  const [ativosSelecionados, setAtivosSelecionados] = useState([])
  const [metaSelecionada, setMetaSelecionada] = useState(null)
  const [yieldMedio, setYieldMedio] = useState('6.0')
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [salvarSimulacao, setSalvarSimulacao] = useState(false)

  useEffect(() => {
    carregarMetas()
    carregarAtivos()
  }, [])

  const carregarMetas = async () => {
    try {
      const response = await metasRendaAPI.listar()
      setMetas(response.data.results || response.data)
    } catch (err) {
      setError('Erro ao carregar metas. Certifique-se de que o backend está rodando.')
      console.error(err)
    }
  }

  const carregarAtivos = async () => {
    try {
      const response = await ativosAPI.listar()
      setAtivos(response.data.results || response.data)
    } catch (err) {
      console.error('Erro ao carregar ativos:', err)
    }
  }

  const handleSimular = async () => {
    if (!metaSelecionada) {
      alert('Selecione uma meta para simular')
      return
    }

    if (ativosSelecionados.length === 0) {
      alert('Selecione pelo menos um ativo para a simulação')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      // Calcular yield médio dos ativos selecionados
      let yieldCalculado = parseFloat(yieldMedio) || null
      
      if (!yieldCalculado && ativosSelecionados.length > 0) {
        // Tentar buscar yields reais da Brapi
        const yields = []
        for (const ativoId of ativosSelecionados) {
          try {
            const ativo = ativos.find(a => a.id === ativoId)
            if (ativo) {
              const dadosBrapi = await ativosAPI.buscarDadosBrapi(ativo.ticker)
              if (dadosBrapi.data.yield_anual) {
                yields.push(dadosBrapi.data.yield_anual)
              }
            }
          } catch (err) {
            console.warn(`Erro ao buscar yield de ${ativoId}:`, err)
          }
        }
        
        if (yields.length > 0) {
          yieldCalculado = yields.reduce((a, b) => a + b, 0) / yields.length
          setYieldMedio(yieldCalculado.toFixed(2))
        }
      }
      
      const dados = {
        yield_medio: yieldCalculado,
        ativos_ids: ativosSelecionados,
        salvar: salvarSimulacao,
      }

      const response = await metasRendaAPI.simular(metaSelecionada.id, dados)
      setResultado(response.data)
    } catch (err) {
      setError('Erro ao executar simulação: ' + (err.response?.data?.detail || err.message))
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const toggleAtivo = (ativoId) => {
    setAtivosSelecionados(prev => {
      if (prev.includes(ativoId)) {
        return prev.filter(id => id !== ativoId)
      } else {
        return [...prev, ativoId]
      }
    })
  }

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(valor)
  }

  const formatarNumero = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(valor)
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
            Simulador de Investimentos em Dividendos
          </h2>
          <p style={{ color: '#475569', marginTop: '0.5rem', fontSize: '1.125rem', lineHeight: '1.7' }}>
            Responda às perguntas abaixo e receba uma simulação personalizada para os seus objetivos.
            Calcule quanto você precisa investir para atingir sua meta de renda mensal.
          </p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="simulacao-form">
          <div className="form-group">
            <label className="form-label" htmlFor="meta">
              Selecione uma Meta *
            </label>
            <select
              id="meta"
              className="form-control"
              value={metaSelecionada?.id || ''}
              onChange={(e) => {
                const meta = metas.find((m) => m.id === parseInt(e.target.value))
                setMetaSelecionada(meta)
                setResultado(null)
              }}
            >
              <option value="">Selecione uma meta</option>
              {metas.map((meta) => (
                <option key={meta.id} value={meta.id}>
                  {meta.nome} - {formatarMoeda(meta.renda_mensal_desejada)}/mês
                </option>
              ))}
            </select>
          </div>

          {metaSelecionada && (
            <div className="meta-detalhes">
              <h3>Detalhes da Meta Selecionada</h3>
              <div className="meta-detalhes-grid">
                <div>
                  <strong>Renda Mensal Desejada:</strong>
                  <span>{formatarMoeda(metaSelecionada.renda_mensal_desejada)}</span>
                </div>
                <div>
                  <strong>Anos para Atingir:</strong>
                  <span>{metaSelecionada.anos_para_atingir} anos</span>
                </div>
                <div>
                  <strong>Inflação Média Anual:</strong>
                  <span>{metaSelecionada.inflacao_media_anual}%</span>
                </div>
                <div>
                  <strong>Reinvestimento:</strong>
                  <span>{metaSelecionada.percentual_reinvestimento}%</span>
                </div>
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">
              Selecione os Ativos para Simulação *
            </label>
            <div className="ativos-selecao" style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', 
              gap: '1rem',
              marginTop: '0.5rem'
            }}>
              {ativos.map((ativo) => (
                <label
                  key={ativo.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '1rem',
                    background: ativosSelecionados.includes(ativo.id) 
                      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)'
                      : 'var(--bg-secondary)',
                    border: `2px solid ${ativosSelecionados.includes(ativo.id) ? 'var(--accent-color)' : 'var(--border-color)'}`,
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={ativosSelecionados.includes(ativo.id)}
                    onChange={() => toggleAtivo(ativo.id)}
                    style={{ marginRight: '0.75rem', width: '20px', height: '20px' }}
                  />
                  <div>
                    <strong>{ativo.ticker}</strong>
                    <div style={{ fontSize: '0.875rem', color: '#64748b' }}>
                      {ativo.nome_empresa}
                    </div>
                  </div>
                </label>
              ))}
            </div>
            {ativos.length === 0 && (
              <p style={{ color: '#475569', marginTop: '0.5rem' }}>
                Nenhum ativo cadastrado. Vá em "Ativos" para cadastrar.
              </p>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="yield_medio">
              Yield Médio Esperado (%)
            </label>
            <input
              type="number"
              id="yield_medio"
              className="form-control"
              value={yieldMedio}
              onChange={(e) => setYieldMedio(e.target.value)}
              step="0.1"
              min="0"
              max="100"
              placeholder="6.0"
            />
            <small style={{ color: '#64748b', fontSize: '0.875rem' }}>
              Yield médio anual esperado. Se não informado, será calculado automaticamente baseado nos ativos selecionados usando dados da Brapi.
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">
              <input
                type="checkbox"
                checked={salvarSimulacao}
                onChange={(e) => setSalvarSimulacao(e.target.checked)}
                style={{ marginRight: '0.5rem' }}
              />
              Salvar resultado da simulação
            </label>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSimular}
            disabled={loading || !metaSelecionada}
          >
            {loading ? 'Calculando...' : 'Executar Simulação'}
          </button>
        </div>

        {resultado && (
          <div className="resultado-simulacao">
            <h3>Resultado da Simulação</h3>
            <div className="resultado-grid">
              <div className="resultado-item highlight">
                <div className="resultado-label">Patrimônio Alvo</div>
                <div className="resultado-value">
                  {formatarMoeda(resultado.patrimonio_alvo)}
                </div>
                <div className="resultado-descricao">
                  Valor total que você precisa acumular
                </div>
              </div>

              <div className="resultado-item highlight">
                <div className="resultado-label">Aporte Mensal Necessário</div>
                <div className="resultado-value">
                  {formatarMoeda(resultado.aporte_mensal)}
                </div>
                <div className="resultado-descricao">
                  Valor que você precisa investir mensalmente
                </div>
              </div>

              <div className="resultado-item">
                <div className="resultado-label">Renda Mensal Ajustada (Futuro)</div>
                <div className="resultado-value">
                  {formatarMoeda(resultado.renda_mensal_ajustada)}
                </div>
                <div className="resultado-descricao">
                  Renda mensal ajustada pela inflação no ano alvo
                </div>
              </div>

              <div className="resultado-item">
                <div className="resultado-label">Yield Médio Usado</div>
                <div className="resultado-value">
                  {formatarNumero(resultado.yield_medio_usado)}%
                </div>
                <div className="resultado-descricao">
                  Yield médio utilizado no cálculo
                </div>
              </div>
            </div>

            <div className="resultado-info">
              <p>
                <strong>Observação:</strong> Estes valores são estimativas baseadas nos
                parâmetros informados. O resultado real pode variar dependendo do desempenho
                dos seus investimentos e das condições de mercado.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SimulacaoPage

