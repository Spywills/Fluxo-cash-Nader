import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Users, DollarSign, Activity, Zap, X, Info } from 'lucide-react';
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card';
import { SkeletonCard } from '../components/ui/Skeleton';
import { Alert } from '../components/ui/Alert';
import { Modal } from '../components/ui/Modal';
import { getBankSimulationGlobal, getBankSimulationWithdrawals } from '../services/api';
import showToast from '../utils/toast';

const KPICard = ({ title, value, icon: Icon, color = 'primary', loading = false, onClick, details }) => {
  const colorClasses = {
    primary: 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-300 text-blue-700 hover:from-blue-100 hover:to-blue-200',
    success: 'bg-gradient-to-br from-green-50 to-green-100 border-green-300 text-green-700 hover:from-green-100 hover:to-green-200',
    danger: 'bg-gradient-to-br from-red-50 to-red-100 border-red-300 text-red-700 hover:from-red-100 hover:to-red-200',
    warning: 'bg-gradient-to-br from-amber-50 to-amber-100 border-amber-300 text-amber-700 hover:from-amber-100 hover:to-amber-200',
  };

  if (loading) return <SkeletonCard />;

  return (
    <button
      onClick={onClick}
      className={`w-full text-left border-2 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:scale-105 cursor-pointer ${colorClasses[color]}`}
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 sm:p-5 gap-3">
        <div className="flex-1 w-full min-w-0">
          <p className="text-xs sm:text-sm font-medium opacity-80 mb-1 sm:mb-2 flex items-center gap-1">
            {title}
            <Info className="h-3 w-3 opacity-50" />
          </p>
          <p className="text-lg sm:text-xl lg:text-2xl font-bold break-words">{value}</p>
        </div>
        <div className={`p-2 sm:p-3 bg-white/60 rounded-lg flex-shrink-0 self-end sm:self-auto`}>
          <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
        </div>
      </div>
    </button>
  );
};

export default function Dashboard() {
  const [bankSummary, setBankSummary] = useState(null);
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryRes, withdrawalsRes] = await Promise.all([
        getBankSimulationGlobal(),
        getBankSimulationWithdrawals()
      ]);
      
      setBankSummary(summaryRes.data);
      setWithdrawals(withdrawalsRes.data.slice(0, 10));
      setError(null);
    } catch (err) {
      setError(err.message || 'Erro ao carregar dashboard');
      showToast.error('Erro', 'Não conseguimos carregar os dados');
      console.error(err);
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

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    });
  };

  const openModal = (title, icon, color, details) => {
    setModalData({ title, icon, color, details });
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalData(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600">Visão geral do sistema em tempo real</p>
        </div>

        {error && (
          <Alert 
            variant="danger"
            title="Erro ao carregar dados"
            description={error}
            className="mb-6"
          />
        )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4 mb-6 sm:mb-8">
        <KPICard
          title="Saldo Geral"
          value={bankSummary ? formatMoney(bankSummary.saldo_geral || 0) : '—'}
          icon={DollarSign}
          color="primary"
          loading={loading}
          onClick={() => openModal('Saldo Geral', DollarSign, 'primary', {
            'Valor Total': formatMoney(bankSummary?.saldo_geral || 0),
            'Total Depósitos': formatMoney(bankSummary?.total_depositos || 0),
            'Total Saques': formatMoney(bankSummary?.total_saques || 0),
            'Clientes Positivos': bankSummary?.clientes_positivos || 0,
            'Clientes Negativos': bankSummary?.clientes_em_negativo || 0,
          })}
        />
        <KPICard
          title="Total Depósitos"
          value={bankSummary ? formatMoney(bankSummary.total_buy_brl || 0) : '—'}
          icon={TrendingUp}
          color="success"
          loading={loading}
          onClick={() => openModal('Total Depósitos', TrendingUp, 'success', {
            'Valor Total': formatMoney(bankSummary?.total_buy_brl || bankSummary?.total_depositos || 0),
            'Número de Depósitos': bankSummary?.total_operations || 0,
            'Média por Depósito': formatMoney((bankSummary?.total_buy_brl || 0) / Math.max(bankSummary?.total_operations || 1, 1)),
          })}
        />
        <KPICard
          title="Total Saques"
          value={bankSummary ? formatMoney(bankSummary.total_sell_brl || 0) : '—'}
          icon={TrendingDown}
          color="danger"
          loading={loading}
          onClick={() => openModal('Total Saques', TrendingDown, 'danger', {
            'Valor Total': formatMoney(bankSummary?.total_sell_brl || bankSummary?.total_saques || 0),
            'Saques Pendentes': withdrawals.filter(w => w.status === 'PENDING' || w.status === 'PENDENTE').length,
            'Saques Aprovados': withdrawals.filter(w => w.status === 'COMPLETED' || w.status === 'APROVADO').length,
          })}
        />
        <KPICard
          title="Clientes Ativos"
          value={bankSummary ? bankSummary.total_clients : '—'}
          icon={Users}
          color="warning"
          loading={loading}
          onClick={() => openModal('Clientes Ativos', Users, 'warning', {
            'Total de Clientes': bankSummary?.total_clients || 0,
            'Clientes com Saldo Positivo': bankSummary?.clientes_positivos || 0,
            'Clientes com Saldo Negativo': bankSummary?.clientes_em_negativo || 0,
            'Taxa de Inadimplência': `${((bankSummary?.clientes_em_negativo || 0) / Math.max(bankSummary?.total_clients || 1, 1) * 100).toFixed(1)}%`,
          })}
        />
        <KPICard
          title="Operações"
          value={bankSummary ? bankSummary.total_operations : '—'}
          icon={Zap}
          color="primary"
          loading={loading}
          onClick={() => openModal('Operações', Zap, 'primary', {
            'Total de Operações': bankSummary?.total_operations || 0,
            'Comprovantes Enviados': bankSummary?.total_comprovantes || 0,
            'Última Atualização': new Date().toLocaleString('pt-BR'),
          })}
        />
      </div>

      {/* Modal de Detalhes */}
      {modalOpen && modalData && (
        <Modal isOpen={modalOpen} onClose={closeModal} title={modalData.title}>
          <div className="space-y-4">
            <div className="flex items-center justify-center mb-6">
              <div className={`p-4 rounded-full ${
                modalData.color === 'primary' ? 'bg-blue-100' :
                modalData.color === 'success' ? 'bg-green-100' :
                modalData.color === 'danger' ? 'bg-red-100' :
                'bg-amber-100'
              }`}>
                <modalData.icon className={`h-12 w-12 ${
                  modalData.color === 'primary' ? 'text-blue-600' :
                  modalData.color === 'success' ? 'text-green-600' :
                  modalData.color === 'danger' ? 'text-red-600' :
                  'text-amber-600'
                }`} />
              </div>
            </div>
            
            <div className="space-y-3">
              {Object.entries(modalData.details).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <span className="text-sm font-medium text-gray-700">{key}</span>
                  <span className="text-sm font-bold text-gray-900">{value}</span>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={closeModal}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-md hover:shadow-lg"
              >
                Fechar
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Últimas Operações */}
      <Card className="shadow-lg">
        <CardHeader className="border-b border-gray-200 bg-white">
          <CardTitle className="text-lg sm:text-xl font-bold text-gray-900">Últimos Saques</CardTitle>
        </CardHeader>
        <CardBody className="p-0">
          {loading ? (
            <div className="p-4 sm:p-6">
              <SkeletonCard />
            </div>
          ) : withdrawals.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-3 sm:px-4 font-semibold text-gray-700 whitespace-nowrap">Data</th>
                    <th className="text-left py-3 px-3 sm:px-4 font-semibold text-gray-700 whitespace-nowrap">Cliente</th>
                    <th className="text-left py-3 px-3 sm:px-4 font-semibold text-gray-700 whitespace-nowrap">Valor</th>
                    <th className="text-left py-3 px-3 sm:px-4 font-semibold text-gray-700 whitespace-nowrap">Status</th>
                    <th className="text-left py-3 px-3 sm:px-4 font-semibold text-gray-700 whitespace-nowrap hidden sm:table-cell">Notas</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {withdrawals.map((withdrawal) => (
                    <tr 
                      key={withdrawal.id} 
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="py-3 px-3 sm:px-4 text-gray-600 text-xs sm:text-sm whitespace-nowrap">
                        {formatDate(withdrawal.date)}
                      </td>
                      <td className="py-3 px-3 sm:px-4 font-medium text-gray-900 text-xs sm:text-sm">
                        {withdrawal.client || 'N/A'}
                      </td>
                      <td className="py-3 px-3 sm:px-4 font-semibold text-red-600 text-xs sm:text-sm whitespace-nowrap">
                        -{formatMoney(withdrawal.amount_brl)}
                      </td>
                      <td className="py-3 px-3 sm:px-4">
                        <span className={`inline-flex items-center px-2 sm:px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
                          withdrawal.status === 'COMPLETED' || withdrawal.status === 'APROVADO'
                            ? 'bg-green-100 text-green-700'
                            : withdrawal.status === 'REJECTED' || withdrawal.status === 'REJEITADO'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}>
                          {withdrawal.status === 'COMPLETED' ? 'Aprovado' : 
                           withdrawal.status === 'REJECTED' ? 'Rejeitado' :
                           withdrawal.status === 'PENDING' ? 'Pendente' : withdrawal.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 sm:px-4 text-gray-600 text-xs sm:text-sm hidden sm:table-cell">
                        {withdrawal.notes || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm sm:text-base">Nenhum saque registrado</p>
            </div>
          )}
        </CardBody>
      </Card>
      </div>
    </div>
  );
}
