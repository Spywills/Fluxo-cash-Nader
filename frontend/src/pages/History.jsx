import React, { useState, useEffect } from 'react';
import { History as HistoryIcon, TrendingUp, TrendingDown, Calendar, User, Globe, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';
import { Alert } from '../components/ui/Alert';
import { SkeletonCard } from '../components/ui/Skeleton';
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card';
import { getClients, getClientHistory, getGlobalHistory } from '../services/api';

export default function History() {
  const [clients, setClients] = useState([]);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewType, setViewType] = useState('global'); // global ou client
  const [selectedClient, setSelectedClient] = useState('');
  const [period, setPeriod] = useState('all');

  useEffect(() => {
    loadClients();
  }, []);

  useEffect(() => {
    loadHistory();
  }, [viewType, selectedClient, period]);

  const loadClients = async () => {
    try {
      const res = await getClients();
      // Defensivo: normalizar clients para array
      const clientsArray = Array.isArray(res.data)
        ? res.data
        : res.data?.clients ?? [];
      setClients(clientsArray);
      if (clientsArray.length > 0) {
        setSelectedClient(clientsArray[0].id);
      }
    } catch (err) {
      setError(err.message || 'Erro ao carregar clientes');
    }
  };

  // Defensivo: garantir que clients é um array
  const safeClients = Array.isArray(clients) ? clients : [];

  const loadHistory = async () => {
    try {
      // Proteger contra selectedClient undefined ou vazio
      if (viewType === 'client' && (!selectedClient || selectedClient === 'undefined')) {
        console.warn('loadHistory - selectedClient é undefined ou vazio');
        setHistory(null);
        return;
      }
      
      setLoading(true);
      let res;
      if (viewType === 'global') {
        res = await getGlobalHistory(period);
      } else {
        res = await getClientHistory(selectedClient, period);
      }
      setHistory(res.data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Erro ao carregar histórico');
    } finally {
      setLoading(false);
    }
  };

  const formatMoney = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-gray-900">Histórico</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </div>
    );
  }

  // Defensivo: normalizar history para ter estrutura consistente
  const safeHistory = history ? {
    history: Array.isArray(history.history) ? history.history : history.historico || [],
    total: history.total || history.total_items || 0,
    total_depositos: history.total_depositos || 0,
    total_saques: history.total_saques || 0,
    saldo_periodo: history.saldo_periodo || 0
  } : null;

  const periodLabels = {
    day: 'Hoje',
    week: 'Esta Semana',
    month: 'Este Mês',
    year: 'Este Ano',
    all: 'Todas'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 flex items-center gap-3">
            <HistoryIcon className="h-8 w-8 text-blue-600" />
            Histórico
          </h1>
          <p className="text-sm text-gray-600 mt-1">Acompanhe todas as transações do sistema</p>
        </div>

        {error && (
          <Alert 
            variant="danger"
            title="Erro ao carregar histórico"
            description={error}
            className="mb-6"
          />
        )}

      {/* Filtros */}
      <Card className="mb-6 shadow-md">
        <CardBody className="p-4 sm:p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Tipo de Visualização */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Visualização</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewType('global')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    viewType === 'global'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Globe className="h-4 w-4" />
                  Global
                </button>
                <button
                  onClick={() => setViewType('client')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    viewType === 'client'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <User className="h-4 w-4" />
                  Cliente
                </button>
              </div>
            </div>

            {/* Seleção de Cliente */}
            {viewType === 'client' && (
              <div>
                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Cliente</label>
                <select
                  value={selectedClient}
                  onChange={(e) => setSelectedClient(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                >
                  {safeClients.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Período */}
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Período</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
              >
                <option value="day">Hoje</option>
                <option value="week">Esta Semana</option>
                <option value="month">Este Mês</option>
                <option value="year">Este Ano</option>
                <option value="all">Todas</option>
              </select>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Stats */}
      {safeHistory && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="border-l-4 border-blue-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Período</p>
                  <p className="text-xl font-bold text-blue-600">{periodLabels[period]}</p>
                </div>
                <Calendar className="h-8 w-8 text-blue-500 opacity-50" />
              </div>
            </CardBody>
          </Card>

          <Card className="border-l-4 border-green-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Depósitos</p>
                  <p className="text-xl font-bold text-green-600">{formatMoney(safeHistory.total_depositos || 0)}</p>
                </div>
                <ArrowUpCircle className="h-8 w-8 text-green-500 opacity-50" />
              </div>
            </CardBody>
          </Card>

          <Card className="border-l-4 border-red-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Saques</p>
                  <p className="text-xl font-bold text-red-600">{formatMoney(safeHistory.total_saques || 0)}</p>
                </div>
                <ArrowDownCircle className="h-8 w-8 text-red-500 opacity-50" />
              </div>
            </CardBody>
          </Card>

          <Card className={`border-l-4 shadow-md hover:shadow-lg transition-shadow ${
            safeHistory.saldo_periodo >= 0 ? 'border-green-500' : 'border-red-500'
          }`}>
            <CardBody className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Saldo</p>
                  <p className={`text-xl font-bold ${
                    safeHistory.saldo_periodo >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatMoney(safeHistory.saldo_periodo || 0)}
                  </p>
                </div>
                {safeHistory.saldo_periodo >= 0 ? (
                  <TrendingUp className="h-8 w-8 text-green-500 opacity-50" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-red-500 opacity-50" />
                )}
              </div>
            </CardBody>
          </Card>
        </div>
      )}

      {/* Transações */}
      {safeHistory && safeHistory.history.length === 0 ? (
        <Card className="shadow-lg">
          <CardBody className="text-center py-16">
            <HistoryIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">Nenhuma transação encontrada</p>
            <p className="text-gray-400 text-sm mt-2">Tente selecionar outro período</p>
          </CardBody>
        </Card>
      ) : (
        <Card className="shadow-lg">
          <CardHeader className="border-b bg-white">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-bold text-gray-900">
                Transações
              </CardTitle>
              <span className="text-sm text-gray-500 font-medium">
                {safeHistory?.total || 0} {safeHistory?.total === 1 ? 'transação' : 'transações'}
              </span>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-200">
                  <tr>
                    {viewType === 'global' && (
                      <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Cliente</th>
                    )}
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Tipo</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Valor</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap hidden sm:table-cell">Data</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap hidden md:table-cell">Descrição</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {safeHistory?.history.map(h => (
                    <tr key={h.id} className="hover:bg-gray-50 transition-colors">
                      {viewType === 'global' && (
                        <td className="py-4 px-4 font-medium text-gray-900">{h.client_name || 'N/A'}</td>
                      )}
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          {h.tipo === 'DEPOSITO' ? (
                            <ArrowUpCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <ArrowDownCircle className="h-4 w-4 text-red-600" />
                          )}
                          <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${
                            h.tipo === 'DEPOSITO'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}>
                            {h.tipo === 'DEPOSITO' ? 'Depósito' : 'Saque'}
                          </span>
                        </div>
                      </td>
                      <td className={`py-4 px-4 font-bold whitespace-nowrap ${
                        h.tipo === 'DEPOSITO' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {h.tipo === 'DEPOSITO' ? '+' : '-'}{formatMoney(h.valor || 0)}
                      </td>
                      <td className="py-4 px-4 text-gray-600 text-xs hidden sm:table-cell whitespace-nowrap">
                        {new Date(h.data_transacao).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric'
                        })}
                        <span className="text-gray-400 ml-2">
                          {new Date(h.data_transacao).toLocaleTimeString('pt-BR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600 text-xs hidden md:table-cell max-w-xs truncate">
                        {h.descricao || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}
      </div>
    </div>
  );
}
