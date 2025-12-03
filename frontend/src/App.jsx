import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import AtivosPage from './pages/AtivosPage'
import HistoricoDividendosPage from './pages/HistoricoDividendosPage'
import MetasRendaPage from './pages/MetasRendaPage'
import SimulacaoPage from './pages/SimulacaoPage'
import TextType from './components/TextType'
import FaultyTerminal from './components/FaultyTerminal'
import PillNav from './components/PillNav'
import LogoLoop from './components/LogoLoop'
import './App.css'

function App() {
  const navItems = [
    { label: 'Home', href: '/' },
    { label: 'Ativos', href: '/ativos' },
    { label: 'Histórico', href: '/historico-dividendos' },
    { label: 'Metas', href: '/metas-renda' },
    { label: 'Simulação', href: '/simulacao' }
  ]

  return (
    <Router>
      <div className="App">
        <ErrorBoundary>
        <PillNav
          items={navItems}
          baseColor="#ffffff"
          pillColor="#003366"
          hoveredPillTextColor="#003366"
          pillTextColor="#ffffff"
          ease="power2.easeOut"
          initialLoadAnimation={true}
        />
        </ErrorBoundary>

        <main className="main-content">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/ativos" element={<AtivosPage />} />
              <Route path="/historico-dividendos" element={<HistoricoDividendosPage />} />
              <Route path="/metas-renda" element={<MetasRendaPage />} />
              <Route path="/simulacao" element={<SimulacaoPage />} />
            </Routes>
          </ErrorBoundary>
        </main>
      </div>
    </Router>
  )
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Erro capturado pelo ErrorBoundary:', error);
    console.error('Error Info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div style={{
          padding: '1rem',
          color: '#ef4444',
          background: 'rgba(239, 68, 68, 0.1)',
          borderRadius: '8px',
          border: '1px solid #ef4444'
        }}>
          Erro ao carregar componente. Verifique o console.
        </div>
      );
    }

    return this.props.children;
  }
}

function HomePage() {
  const [showTerminal, setShowTerminal] = React.useState(true)
  const [hasError, setHasError] = React.useState(false)

  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (document.querySelector('.hero-content')?.textContent === '') {
        setHasError(true)
      }
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="home-container">
      <div className="hero-section-with-bg">
        <div className="hero-background-image">
          <img 
            src="https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1920&h=1080&fit=crop" 
            alt="Background"
            className="hero-bg-img"
          />
          <div className="hero-overlay"></div>
        </div>
        <div className="terminal-background">
          {showTerminal && !hasError ? (
            <ErrorBoundary>
              <FaultyTerminal
                scale={1.5}
                gridMul={[2, 1]}
                digitSize={1.2}
                timeScale={0.3}
                scanlineIntensity={0.2}
                glitchAmount={0.3}
                flickerAmount={0.2}
                noiseAmp={0.05}
                curvature={0.03}
                tint="#ffffff"
                mouseReact={true}
                mouseStrength={0.15}
                pageLoadAnimation={true}
                brightness={0.4}
              />
            </ErrorBoundary>
          ) : (
            <div style={{
              background: 'linear-gradient(135deg, rgba(0, 51, 102, 0.8) 0%, rgba(0, 77, 153, 0.6) 100%)',
              opacity: 0.3,
              width: '100%',
              height: '100%'
            }} />
          )}
        </div>
        <div className="hero-content">
          <ErrorBoundary fallback={<h1 className="hero-title">Planejador de Dividendos</h1>}>
            <TextType
              text={[
                "Planejador de Dividendos",
                "Sua Jornada para a Liberdade Financeira",
                "Simule seus Investimentos com Inteligência"
              ]}
              as="h1"
              typingSpeed={75}
              pauseDuration={2000}
              deletingSpeed={50}
              loop={true}
              showCursor={true}
              cursorCharacter="|"
              className="hero-title"
              textColors={['#ffffff', '#FFD700', '#ffffff']}
            />
          </ErrorBoundary>
          <p className="hero-subtitle">
            Planeje sua independência financeira através de investimentos em dividendos.
            Simule, acompanhe e alcance suas metas de renda mensal com dados reais.
          </p>
        </div>
      </div>

      <div className="container">
        <div className="features-intro">
          <h2 className="features-title">Recursos Principais</h2>
          <p className="features-subtitle">
            Tudo que você precisa para planejar sua independência financeira
          </p>
        </div>
        
        <div className="features-loop-container">
          <LogoLoop
            logos={[
              {
                node: (
                  <div className="feature-card-loop">
                    <div className="feature-image-wrapper">
                      <img 
                        src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop" 
                        alt="Gerenciar Ativos"
                        className="feature-image"
                      />
                    </div>
                    <h3>Gerenciar Ativos</h3>
                    <p>Cadastre e gerencie seus ativos. Busque dados reais na Brapi.</p>
                  </div>
                ),
                title: 'Gerenciar Ativos'
              },
              {
                node: (
                  <div className="feature-card-loop">
                    <div className="feature-image-wrapper">
                      <img 
                        src="https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=400&h=300&fit=crop" 
                        alt="Histórico de Dividendos"
                        className="feature-image"
                      />
                    </div>
                    <h3>Histórico de Dividendos</h3>
                    <p>Registre ou importe automaticamente o histórico de dividendos.</p>
                  </div>
                ),
                title: 'Histórico de Dividendos'
              },
              {
                node: (
                  <div className="feature-card-loop">
                    <div className="feature-image-wrapper">
                      <img 
                        src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop" 
                        alt="Metas de Renda"
                        className="feature-image"
                      />
                    </div>
                    <h3>Metas de Renda</h3>
                    <p>Defina suas metas de renda mensal. Configure prazos e inflação.</p>
                  </div>
                ),
                title: 'Metas de Renda'
              },
              {
                node: (
                  <div className="feature-card-loop">
                    <div className="feature-image-wrapper">
                      <img 
                        src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=300&fit=crop" 
                        alt="Simulação Inteligente"
                        className="feature-image"
                      />
                    </div>
                    <h3>Simulação Inteligente</h3>
                    <p>Calcule quanto investir para atingir suas metas com dados reais.</p>
                  </div>
                ),
                title: 'Simulação Inteligente'
              }
            ]}
            speed={50}
            direction="left"
            logoHeight={320}
            gap={32}
            hoverSpeed={20}
            fadeOut={true}
            fadeOutColor="#f5f5f5"
            scaleOnHover={true}
            ariaLabel="Recursos principais"
            className="features-logoloop"
          />
        </div>
      </div>
    </div>
  )
}

export default App
