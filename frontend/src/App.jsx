
import React, { useState, useEffect } from 'react';
import { Toaster } from 'sonner';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients_pro';
import Withdrawals from './pages/Withdrawals';
import History from './pages/History';
import BankSummary from './pages/BankSummary';
import Users from './pages/Users';
import Login from './pages/Login';
import { Alert } from './components/ui/Alert';
import { healthCheck } from './services/api';
import './index.css';

function App() {
  // Estado de autenticação
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Recuperar página atual do localStorage ou usar dashboard como padrão
  const [currentPage, setCurrentPage] = useState(() => {
    return localStorage.getItem('currentPage') || 'dashboard';
  });
  const [connectionError, setConnectionError] = useState(null);
  const [isOnline, setIsOnline] = useState(true);

  // Verificar autenticação ao carregar
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('auth_user');
    
    if (token && user) {
      try {
        setCurrentUser(JSON.parse(user));
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      }
    }
    
    setAuthLoading(false);
  }, []);

  // Salvar página atual no localStorage quando mudar
  const handlePageChange = (page) => {
    setCurrentPage(page);
    localStorage.setItem('currentPage', page);
  };

  useEffect(() => {
    // Verificar conexão com backend
    const checkConnection = async () => {
      try {
        await healthCheck();
        setIsOnline(true);
        setConnectionError(null);
      } catch (err) {
        setIsOnline(false);
        setConnectionError('❌ Falha na conexão com o backend (http://127.0.0.1:8000)');
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Verificar a cada 30s

    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'clients':
        return <Clients />;
      case 'withdrawals':
        return <Withdrawals />;
      case 'history':
        return <History />;
      case 'bank-summary':
        return <BankSummary />;
      case 'users':
        // Apenas admins podem acessar
        if (currentUser?.is_admin) {
          return <Users />;
        }
        return <Dashboard />;
      default:
        return <Dashboard />;
    }
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setCurrentUser(null);
    setIsAuthenticated(false);
  };

  // Mostrar loading enquanto verifica autenticação
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Carregando...</div>
      </div>
    );
  }

  // Mostrar tela de login se não autenticado
  if (!isAuthenticated) {
    return (
      <>
        <Login onLoginSuccess={handleLoginSuccess} />
        <Toaster position="bottom-right" richColors />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col">
      <Header currentUser={currentUser} onLogout={handleLogout} />
      <Navigation currentPage={currentPage} onPageChange={handlePageChange} currentUser={currentUser} />
      
      <main className="flex-1">
        {!isOnline && (
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 pt-6">
            <Alert 
              variant="danger"
              title="Conexão com Backend Perdida"
              description="Não conseguimos conectar com o backend. Verifique se o servidor está rodando em http://127.0.0.1:8000"
            />
          </div>
        )}
        {renderPage()}
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white border-t border-slate-700">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-center sm:text-left">
              <p className="text-sm sm:text-base font-semibold">💰 FLUXO CASH</p>
              <p className="text-xs text-slate-400 mt-1">Sistema de Gestão Financeira</p>
            </div>
            <div className="flex items-center gap-4 text-xs sm:text-sm">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                isOnline ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
                {isOnline ? 'Online' : 'Offline'}
              </div>
              <span className="text-slate-500">© 2025</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Toast Provider */}
      <Toaster position="bottom-right" richColors />
    </div>
  );
}

export default App;
