import React, { useState, useEffect } from 'react';
import { Building2, TrendingUp, TrendingDown, AlertTriangle, ChevronRight, X } from 'lucide-react';
import { Alert } from '../components/ui/Alert';
import { SkeletonCard } from '../components/ui/Skeleton';
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card';
import { Modal } from '../components/ui/Modal';
import { getGlobalBalance, getClients } from '../services/api';

export default function BankSummary() {
  const [summary, setSummary] = useState(null);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNegativeModal, setShowNegativeModal] = useState(false);

  useEffect(() => {
    loadData();
    // Refrescar dados a cada 30 segundos
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryRes, clientsRes] = await Promise.all([
        getGlobalBalance(),
        getClients()
      ]);

      setSummary(summaryRes.data);

      // Normalizar clientes para array
      const clientsArray = Array.isArray(clientsRes.data)
        ? clientsRes.data
        : clientsRes.data?.clients ?? [];

      // Usar diretamente os dados do cliente (já tem saldo)
      setClients(clientsArray);
      setError(null);
    } catch (err) {
      setError(err.message || 'Erro ao carregar dados');
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
          <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-gray-900">Resumo</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        </div>
      </div>
    );
  }

  // Defensivo: garantir que clients é um array
  const safeClients = Array.isArray(clients) ? clients : [];
  
  // Filtrar clientes com saldo negativo (devedores)
  const negativeClients = safeClients.filter(c => {
    const saldo = c.saldo || c.saldo_atual || 0;
    return saldo < 0;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 flex items-center gap-3">
            <Building2 className="h-8 w-8 text-blue-600" />
            Resumo
          </h1>
          <p className="text-sm text-gray-600 mt-1">Visão consolidada do sistema</p>
        </div>

        {error && (
          <Alert 
            variant="danger"
            title="Erro ao carregar dados"
            description={error}
            className="mb-6"
          />
        )}

        {summary && (
          <>
            {/* Cards Principais - Apenas Depósitos e Saques */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mb-6">
              {/* Card Depósitos */}
              <Card className="border-l-4 border-green-500 shadow-lg hover:shadow-xl transition-shadow">
                <CardBody className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Total Depósitos</p>
                      <p className="text-3xl sm:text-4xl font-bold text-green-600">
                        {formatMoney(summary.total_buy_brl || summary.total_depositos || 0)}
                      </p>
                    </div>
                    <div className="p-3 bg-green-100 rounded-xl">
                      <TrendingUp className="h-8 w-8 text-green-600" />
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">Valor total depositado no sistema</p>
                </CardBody>
              </Card>

              {/* Card Saques */}
              <Card className="border-l-4 border-red-500 shadow-lg hover:shadow-xl transition-shadow">
                <CardBody className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Total Saques</p>
                      <p className="text-3xl sm:text-4xl font-bold text-red-600">
                        {formatMoney(summary.total_sell_brl || summary.total_saques || 0)}
                      </p>
                    </div>
                    <div className="p-3 bg-red-100 rounded-xl">
                      <TrendingDown className="h-8 w-8 text-red-600" />
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">Valor total sacado do sistema</p>
                </CardBody>
              </Card>
            </div>

            {/* Card Clientes Negativos - Clicável */}
            {negativeClients.length > 0 && (
              <button
                onClick={() => setShowNegativeModal(true)}
                className="w-full text-left"
              >
                <Card className="border-l-4 border-orange-500 shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] cursor-pointer">
                  <CardBody className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="p-2 bg-orange-100 rounded-lg">
                            <AlertTriangle className="h-6 w-6 text-orange-600" />
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Clientes Negativos</p>
                            <p className="text-2xl font-bold text-orange-600">{negativeClients.length}</p>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {negativeClients.length === 1 ? 'Cliente com' : 'Clientes com'} saldo devedor
                        </p>
                        <div className="flex items-center gap-2 text-blue-600 text-sm font-medium">
                          <span>Ver detalhes</span>
                          <ChevronRight className="h-4 w-4" />
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              </button>
            )}

            {/* Mensagem quando não há clientes negativos */}
            {negativeClients.length === 0 && (
              <Card className="border-l-4 border-green-500 shadow-lg">
                <CardBody className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <AlertTriangle className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Clientes Negativos</p>
                      <p className="text-lg font-bold text-green-600">Nenhum cliente devedor</p>
                      <p className="text-sm text-gray-600 mt-1">Todos os clientes estão em dia</p>
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}
          </>
        )}

        {/* Modal de Clientes Negativos */}
        {showNegativeModal && (
          <Modal 
            isOpen={showNegativeModal} 
            onClose={() => setShowNegativeModal(false)} 
            title="Clientes com Saldo Negativo"
            size="lg"
          >
            <div className="space-y-3">
              {negativeClients.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Nenhum cliente com saldo negativo</p>
              ) : (
                <>
                  <div className="mb-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                    <div className="flex items-center gap-2 text-orange-700">
                      <AlertTriangle className="h-5 w-5" />
                      <p className="text-sm font-medium">
                        {negativeClients.length} {negativeClients.length === 1 ? 'cliente está' : 'clientes estão'} com saldo devedor
                      </p>
                    </div>
                  </div>

                  {negativeClients.map(client => {
                    const saldo = client.saldo || client.saldo_atual || 0;
                    return (
                      <div 
                        key={client.id} 
                        className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-200 hover:bg-red-100 transition-colors"
                      >
                        <div className="flex-1">
                          <p className="font-semibold text-gray-900">{client.name}</p>
                          <p className="text-xs text-gray-600 mt-1">ID: {client.id}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-red-600">
                            -{formatMoney(Math.abs(saldo))}
                          </p>
                          <p className="text-xs text-gray-600 mt-1">Saldo devedor</p>
                        </div>
                      </div>
                    );
                  })}

                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-gray-700">Total Devedor:</span>
                      <span className="text-xl font-bold text-red-600">
                        -{formatMoney(negativeClients.reduce((sum, c) => {
                          const saldo = c.saldo || c.saldo_atual || 0;
                          return sum + Math.abs(saldo);
                        }, 0))}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <button
                onClick={() => setShowNegativeModal(false)}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-md hover:shadow-lg"
              >
                Fechar
              </button>
            </div>
          </Modal>
        )}
      </div>
    </div>
  );
}
