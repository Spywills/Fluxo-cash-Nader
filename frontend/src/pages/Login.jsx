import React, { useState } from 'react';
import { toast } from 'sonner';
import { login } from '../services/api';

function Login({ onLoginSuccess }) {
  const [loading, setLoading] = useState(false);
  
  // Login form
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      toast.error('Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const response = await login(username, password);
      const { access_token, user } = response.data;
      
      // Salvar token e usuário no localStorage
      localStorage.setItem('auth_token', access_token);
      localStorage.setItem('auth_user', JSON.stringify(user));
      
      toast.success(`Bem-vindo, ${user.full_name || user.username}!`);
      onLoginSuccess(user);
    } catch (error) {
      console.error('Erro no login:', error);
      toast.error(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl mb-4 shadow-lg">
            <span className="text-3xl">💰</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">FLUXO CASH</h1>
          <p className="text-slate-400">Sistema de Gestão Financeira</p>
        </div>

        {/* Card de Login */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6 text-center">
            Entrar no Sistema
          </h2>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Usuário
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                  placeholder="Digite seu usuário"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Senha
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                  placeholder="Digite sua senha"
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </button>
            </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-slate-400 text-sm">
          <p>© 2025 FLUXO CASH - Todos os direitos reservados</p>
        </div>
      </div>
    </div>
  );
}

export default Login;
