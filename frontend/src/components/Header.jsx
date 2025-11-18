import React from 'react';
import { Wallet, Bell, LogOut, User } from 'lucide-react';

export default function Header({ currentUser, onLogout }) {
  const today = new Date().toLocaleDateString('pt-BR', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  return (
    <header className="bg-gradient-to-r from-slate-800 via-slate-900 to-slate-800 shadow-xl border-b border-slate-700">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5">
        <div className="flex items-center justify-between">
          {/* Logo e Título */}
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-2 sm:p-3 shadow-lg">
              <Wallet className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white flex items-center gap-2">
                💰 FLUXO CASH
              </h1>
              <p className="text-slate-300 text-xs sm:text-sm mt-0.5 hidden sm:block">Sistema de Gestão Financeira</p>
            </div>
          </div>
          
          {/* Info e Ações */}
          <div className="flex items-center gap-3 sm:gap-4">
            <div className="text-right text-slate-300 hidden md:block">
              <p className="text-xs font-medium opacity-75">📅 Hoje</p>
              <p className="text-xs sm:text-sm font-semibold capitalize">{today}</p>
            </div>

            {/* User Info */}
            {currentUser && (
              <div className="flex items-center gap-2 bg-slate-700/50 px-3 py-2 rounded-lg">
                <User className="h-4 w-4 text-slate-300" />
                <div className="text-right hidden sm:block">
                  <p className="text-xs text-slate-400">Usuário</p>
                  <p className="text-sm font-semibold text-white">
                    {currentUser.full_name || currentUser.username}
                  </p>
                </div>
              </div>
            )}

            <button className="bg-slate-700/50 hover:bg-slate-700 text-white p-2 sm:p-2.5 rounded-lg transition-all shadow-md hover:shadow-lg relative">
              <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center font-bold">
                0
              </span>
            </button>

            {/* Logout Button */}
            {onLogout && (
              <button
                onClick={onLogout}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-400 hover:text-red-300 p-2 sm:p-2.5 rounded-lg transition-all shadow-md hover:shadow-lg flex items-center gap-2"
                title="Sair"
              >
                <LogOut className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="hidden sm:inline text-sm font-medium">Sair</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Divider line */}
      <div className="h-0.5 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-30"></div>
    </header>
  );
}
