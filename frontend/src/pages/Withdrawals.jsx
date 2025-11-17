import React, { useState, useEffect } from 'react';
import { Plus, Filter, Search, Trash2, Eye, CheckCircle, XCircle, Clock, Ban, TrendingDown } from 'lucide-react';
import { Alert } from '../components/ui/Alert';
import { SkeletonCard } from '../components/ui/Skeleton';
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import showToast from '../utils/toast';
import { getClients, createWithdrawal, getGlobalWithdrawals, deleteWithdrawal, updateWithdrawal } from '../services/api';

export default function Withdrawals() {
  const [clients, setClients] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWithdrawal, setSelectedWithdrawal] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [formData, setFormData] = useState({
    client_id: '',
    valor: '',
    descricao: '',
    admin_notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [clientsRes, withdrawalsRes] = await Promise.all([
        getClients(),
        getGlobalWithdrawals()
      ]);
      // Defensivo: normalizar clients para array
      const clientsArray = Array.isArray(clientsRes.data)
        ? clientsRes.data
        : clientsRes.data?.clients ?? [];
      setClients(clientsArray);
      
      // Defensivo: normalizar withdrawals para array
      const withdrawalsArray = Array.isArray(withdrawalsRes.data)
        ? withdrawalsRes.data
        : withdrawalsRes.data?.withdrawals ?? [];
      setWithdrawals(withdrawalsArray);
      setError(null);
    } catch (err) {
      setError(err.message || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  // Defensivo: garantir que clients e withdrawals são arrays
  const safeClients = Array.isArray(clients) ? clients : [];
  const safeWithdrawals = Array.isArray(withdrawals) ? withdrawals : [];

  const handleCreateWithdrawal = async (e) => {
    e.preventDefault();
    
    // Proteger contra client_id undefined ou vazio
    if (!formData.client_id || formData.client_id === 'undefined') {
      setError('Erro: Selecione um cliente válido');
      console.warn('handleCreateWithdrawal - client_id é undefined:', formData.client_id);
      return;
    }

    try {
      await createWithdrawal(formData.client_id, {
        valor: parseFloat(formData.valor),
        descricao: formData.descricao,
        admin_notes: formData.admin_notes
      });
      showToast.success('Sucesso', 'Saque criado com sucesso!');
      setFormData({ client_id: '', valor: '', descricao: '', admin_notes: '' });
      setShowForm(false);
      loadData();
    } catch (err) {
      setError(err.message || 'Erro ao criar saque');
    }
  };

  const handleDeleteWithdrawal = async (clientId, withdrawalId) => {
    // Proteger contra clientId undefined
    if (!clientId || clientId === 'undefined') {
      setError('Erro: Cliente não identificado. Recarregue a página.');
      console.warn('handleDeleteWithdrawal - clientId é undefined:', clientId);
      return;
    }
    
    if (window.confirm('Tem certeza que deseja cancelar este saque?')) {
      try {
        await deleteWithdrawal(clientId, withdrawalId);
        showToast.success('Sucesso', 'Saque cancelado!');
        loadData();
      } catch (err) {
        setError(err.message || 'Erro ao cancelar saque');
      }
    }
  };

  const handleUpdateStatus = async (clientId, withdrawalId, newStatus) => {
    // Proteger contra clientId undefined
    if (!clientId || clientId === 'undefined') {
      setError('Erro: Cliente não identificado. Recarregue a página.');
      console.warn('handleUpdateStatus - clientId é undefined:', clientId);
      return;
    }
    
    try {
      await updateWithdrawal(clientId, withdrawalId, { status: newStatus });
      showToast.success('Sucesso', 'Status atualizado!');
      loadData();
    } catch (err) {
      setError(err.message || 'Erro ao atualizar status');
    }
  };

  const filteredWithdrawals = safeWithdrawals.filter(w => {
    // Filtro por status
    if (filter !== 'all' && w.status !== filter) return false;
    
    // Filtro por busca
    if (searchTerm) {
      const client = safeClients.find(c => c.id === w.client_id);
      const clientName = (w.client || client?.name || '').toLowerCase();
      const notes = (w.notes || w.descricao || '').toLowerCase();
      const search = searchTerm.toLowerCase();
      return clientName.includes(search) || notes.includes(search);
    }
    
    return true;
  });

  const getStatusIcon = (status) => {
    switch(status) {
      case 'APROVADO': return <CheckCircle className="h-4 w-4" />;
      case 'REJEITADO': return <XCircle className="h-4 w-4" />;
      case 'PENDENTE': return <Clock className="h-4 w-4" />;
      case 'CANCELADO': return <Ban className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'APROVADO': return 'bg-green-100 text-green-700 border-green-300';
      case 'REJEITADO': return 'bg-red-100 text-red-700 border-red-300';
      case 'PENDENTE': return 'bg-amber-100 text-amber-700 border-amber-300';
      case 'CANCELADO': return 'bg-gray-100 text-gray-700 border-gray-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const formatMoney = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const openDetailsModal = (withdrawal) => {
    setSelectedWithdrawal(withdrawal);
    setShowDetailsModal(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6 text-gray-900">💸 Saques</h2>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  // Estatísticas
  const stats = {
    total: safeWithdrawals.length,
    pendentes: safeWithdrawals.filter(w => w.status === 'PENDENTE').length,
    aprovados: safeWithdrawals.filter(w => w.status === 'APROVADO').length,
    rejeitados: safeWithdrawals.filter(w => w.status === 'REJEITADO').length,
    valorTotal: safeWithdrawals.reduce((sum, w) => sum + (w.amount_brl || w.valor || 0), 0),
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 flex items-center gap-2">
              <TrendingDown className="h-8 w-8 text-red-600" />
              Saques
            </h1>
            <p className="text-sm text-gray-600 mt-1">Gerencie todos os saques do sistema</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-4 sm:px-6 py-2.5 sm:py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            <Plus className="h-5 w-5" />
            Novo Saque
          </button>
        </div>

        {error && (
          <Alert 
            variant="danger"
            title="Erro"
            description={error}
            className="mb-6"
          />
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-6">
          <Card className="border-l-4 border-blue-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <p className="text-xs sm:text-sm text-gray-600 mb-1">Total de Saques</p>
              <p className="text-xl sm:text-2xl font-bold text-gray-900">{stats.total}</p>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-amber-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <p className="text-xs sm:text-sm text-gray-600 mb-1">Pendentes</p>
              <p className="text-xl sm:text-2xl font-bold text-amber-600">{stats.pendentes}</p>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-green-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <p className="text-xs sm:text-sm text-gray-600 mb-1">Aprovados</p>
              <p className="text-xl sm:text-2xl font-bold text-green-600">{stats.aprovados}</p>
            </CardBody>
          </Card>
          <Card className="border-l-4 border-red-500 shadow-md hover:shadow-lg transition-shadow">
            <CardBody className="p-4">
              <p className="text-xs sm:text-sm text-gray-600 mb-1">Valor Total</p>
              <p className="text-lg sm:text-xl font-bold text-red-600">{formatMoney(stats.valorTotal)}</p>
            </CardBody>
          </Card>
        </div>

      {/* Formulário */}
      {showForm && (
        <Card className="mb-6 shadow-lg border-t-4 border-blue-500">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b">
            <CardTitle className="text-lg font-bold text-gray-900">Novo Saque</CardTitle>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleCreateWithdrawal} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cliente *</label>
                  <select
                    value={formData.client_id}
                    onChange={(e) => setFormData({...formData, client_id: e.target.value})}
                    required
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  >
                    <option value="">Selecione um Cliente</option>
                    {safeClients.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Valor (R$) *</label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="0,00"
                    value={formData.valor}
                    onChange={(e) => setFormData({...formData, valor: e.target.value})}
                    required
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Descrição</label>
                <textarea
                  placeholder="Motivo do saque, informações adicionais..."
                  value={formData.descricao}
                  onChange={(e) => setFormData({...formData, descricao: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Anotações Internas</label>
                <textarea
                  placeholder="Notas visíveis apenas para administradores..."
                  value={formData.admin_notes}
                  onChange={(e) => setFormData({...formData, admin_notes: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  rows="2"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg font-semibold shadow-md hover:shadow-lg transition-all"
                >
                  Criar Saque
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition-all"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Filtros e Busca */}
      <Card className="mb-6 shadow-md">
        <CardBody className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Busca */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por cliente ou descrição..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
            
            {/* Filtros */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2 lg:pb-0">
              <Filter className="h-5 w-5 text-gray-500 flex-shrink-0" />
              {[
                { value: 'all', label: 'Todos', color: 'bg-gray-200 text-gray-700 hover:bg-gray-300' },
                { value: 'PENDENTE', label: 'Pendentes', color: 'bg-amber-100 text-amber-700 hover:bg-amber-200' },
                { value: 'APROVADO', label: 'Aprovados', color: 'bg-green-100 text-green-700 hover:bg-green-200' },
                { value: 'REJEITADO', label: 'Rejeitados', color: 'bg-red-100 text-red-700 hover:bg-red-200' },
              ].map(({ value, label, color }) => (
                <button
                  key={value}
                  onClick={() => setFilter(value)}
                  className={`px-3 sm:px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap text-sm ${
                    filter === value
                      ? 'ring-2 ring-blue-500 shadow-md'
                      : ''
                  } ${color}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          
          {/* Contador de resultados */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              Mostrando <span className="font-semibold text-gray-900">{filteredWithdrawals.length}</span> de <span className="font-semibold text-gray-900">{safeWithdrawals.length}</span> saques
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Tabela */}
      {filteredWithdrawals.length === 0 ? (
        <Card className="shadow-lg">
          <CardBody className="text-center py-16">
            <TrendingDown className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">Nenhum saque encontrado</p>
            <p className="text-gray-400 text-sm mt-2">
              {searchTerm || filter !== 'all' 
                ? 'Tente ajustar os filtros de busca' 
                : 'Crie um novo saque para começar'}
            </p>
          </CardBody>
        </Card>
      ) : (
        <Card className="shadow-lg">
          <CardBody className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-200">
                  <tr>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Cliente</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Valor</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Status</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap hidden sm:table-cell">Data</th>
                    <th className="text-left py-4 px-4 font-semibold text-gray-700 whitespace-nowrap hidden md:table-cell">Descrição</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-700 whitespace-nowrap">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredWithdrawals.map(w => {
                    const client = safeClients.find(c => c.id === w.client_id);
                    const amount = w.amount_brl || w.valor || 0;
                    const dateStr = w.date || w.created_at || w.data_saque;
                    const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('pt-BR', { year: 'numeric', month: '2-digit', day: '2-digit' }) : 'Sem data';
                    
                    return (
                      <tr key={w.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4 font-medium text-gray-900">
                          {w.client || client?.name || (w.client_id ? `Cliente #${w.client_id}` : 'Cliente Desconhecido')}
                        </td>
                        <td className="py-4 px-4 font-bold text-red-600 whitespace-nowrap">
                          {formatMoney(amount)}
                        </td>
                        <td className="py-4 px-4">
                          <select
                            value={w.status}
                            onChange={(e) => handleUpdateStatus(w.client_id, w.id, e.target.value)}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border-2 cursor-pointer transition-all hover:shadow-md ${getStatusColor(w.status)}`}
                          >
                            <option value="PENDENTE">PENDENTE</option>
                            <option value="APROVADO">APROVADO</option>
                            <option value="REJEITADO">REJEITADO</option>
                            <option value="CANCELADO">CANCELADO</option>
                          </select>
                        </td>
                        <td className="py-4 px-4 text-gray-600 text-xs hidden sm:table-cell whitespace-nowrap">
                          {formattedDate}
                        </td>
                        <td className="py-4 px-4 text-gray-600 text-xs hidden md:table-cell max-w-xs truncate">
                          {w.notes || w.descricao || '—'}
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => openDetailsModal(w)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Ver detalhes"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteWithdrawal(w.client_id, w.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Excluir"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Modal de Detalhes */}
      {showDetailsModal && selectedWithdrawal && (
        <Modal isOpen={showDetailsModal} onClose={() => setShowDetailsModal(false)} title="Detalhes do Saque">
          <div className="space-y-4">
            <div className="flex items-center justify-center mb-4">
              <div className={`p-4 rounded-full ${
                selectedWithdrawal.status === 'APROVADO' ? 'bg-green-100' :
                selectedWithdrawal.status === 'REJEITADO' ? 'bg-red-100' :
                selectedWithdrawal.status === 'PENDENTE' ? 'bg-amber-100' :
                'bg-gray-100'
              }`}>
                {getStatusIcon(selectedWithdrawal.status)}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Cliente</span>
                <span className="text-sm font-bold text-gray-900">
                  {selectedWithdrawal.client || safeClients.find(c => c.id === selectedWithdrawal.client_id)?.name || 'N/A'}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Valor</span>
                <span className="text-sm font-bold text-red-600">
                  {formatMoney(selectedWithdrawal.amount_brl || selectedWithdrawal.valor || 0)}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Status</span>
                <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${getStatusColor(selectedWithdrawal.status)}`}>
                  {selectedWithdrawal.status}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Data</span>
                <span className="text-sm font-bold text-gray-900">
                  {new Date(selectedWithdrawal.date || selectedWithdrawal.created_at).toLocaleString('pt-BR')}
                </span>
              </div>
              {(selectedWithdrawal.notes || selectedWithdrawal.descricao) && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700 block mb-2">Descrição</span>
                  <p className="text-sm text-gray-900">{selectedWithdrawal.notes || selectedWithdrawal.descricao}</p>
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-md hover:shadow-lg"
              >
                Fechar
              </button>
            </div>
          </div>
        </Modal>
      )}
      </div>
    </div>
  );
}
