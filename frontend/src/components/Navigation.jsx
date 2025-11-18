import React from 'react';
import { LayoutDashboard, Users, TrendingDown, History, Building2, UserCog } from 'lucide-react';

export default function Navigation({ currentPage, onPageChange, currentUser }) {
  const pages = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'clients', label: 'Clientes', icon: Users },
    { id: 'withdrawals', label: 'Saques', icon: TrendingDown },
    { id: 'history', label: 'Histórico', icon: History },
    { id: 'bank-summary', label: 'Resumo', icon: Building2 },
  ];

  // Adicionar página de usuários apenas para admins
  if (currentUser?.is_admin) {
    pages.push({ id: 'users', label: 'Usuários', icon: UserCog });
  }

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200 sticky top-0 z-40">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex gap-1 overflow-x-auto scrollbar-hide py-0">
          {pages.map(page => {
            const Icon = page.icon;
            const isActive = currentPage === page.id;
            
            return (
              <button
                key={page.id}
                onClick={() => onPageChange(page.id)}
                className={`px-4 sm:px-6 py-3 sm:py-4 whitespace-nowrap font-medium transition-all duration-200 flex items-center gap-2 relative group text-sm sm:text-base ${
                  isActive
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="hidden sm:inline">{page.label}</span>
                {isActive && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-600 via-blue-500 to-blue-600"></div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
