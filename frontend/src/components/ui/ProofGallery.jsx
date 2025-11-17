import React, { useState, useEffect } from 'react';
import { Download, Trash2, AlertCircle, FileText, Image as ImageIcon, DollarSign, Check } from 'lucide-react';
import { Button } from './Button';
import { Badge } from './Badge';
import { Alert } from './Alert';
import { Skeleton } from './Skeleton';
import { getClientProofs, deleteProof } from '../../services/api';
import api from '../../services/api';
import showToast from '../../utils/toast';

/**
 * ProofGallery - Galeria de comprovantes enviados
 * @param {string} clientId - ID do cliente
 * @param {function} onRefresh - Callback ao atualizar
 * @param {function} onBalanceUpdate - Callback ao depositar (atualiza saldo do cliente)
 */
export const ProofGallery = ({ clientId, onRefresh = () => {}, onBalanceUpdate = () => {} }) => {
  const [proofs, setProofs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [depositing, setDepositing] = useState(null);

  useEffect(() => {
    loadProofs();
  }, [clientId]);

  const loadProofs = async () => {
    try {
      // Proteger contra clientId undefined ou inválido
      if (!clientId || clientId === 'undefined') {
        setError('Erro: Cliente não identificado');
        console.warn('loadProofs - clientId é undefined ou vazio:', clientId);
        setLoading(false);
        return;
      }
      
      setLoading(true);
      const response = await getClientProofs(clientId);
      setProofs(response.data.proofs || []);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar comprovantes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (proofId) => {
    if (!window.confirm('Deletar este comprovante?')) return;

    try {
      await deleteProof(proofId);
      
      // ✅ Remove imediatamente do estado
      setProofs(prev => prev.filter(p => p.id !== proofId));
      
      showToast.success('Comprovante deletado', 'com sucesso');
      
      // ✅ Callback para atualizar saldo e dados do cliente
      onRefresh?.();
    } catch (err) {
      console.error('Erro ao deletar:', err);
      showToast.error('Erro', err.response?.data?.detail || 'ao deletar comprovante');
    }
  };

  // 🌟 NOVO: Criar depósito
  const handleDeposit = async (proofId, value) => {
    setDepositing(proofId);
    try {
      const resp = await api.post(`/deposits/proofs/${proofId}`);

      if (!resp || resp.status >= 400) throw new Error('Erro ao criar depósito');

      showToast.success('Depósito criado!', `R$ ${value.toLocaleString('pt-BR')}`);

      // Atualizar status da prova
      setProofs(prev => prev.map(p => 
        p.id === proofId ? { ...p, deposited: true } : p
      ));

      // 🔄 Callback para atualizar saldo no componente pai
      onBalanceUpdate?.(resp.data?.client_saldo);
      onRefresh?.();
    } catch (err) {
      // Mensagem específica para comprovante já creditado
      const errorMsg = err.response?.data?.error || err.response?.data?.detail || 'ao criar depósito';
      showToast.error('Erro', errorMsg);
      console.error(err);
    } finally {
      setDepositing(null);
    }
  };

  const getFileIcon = (fileType) => {
    if (fileType.includes('pdf')) {
      return <FileText className="w-4 h-4 text-red-500" />;
    }
    if (fileType.includes('image')) {
      return <ImageIcon className="w-4 h-4 text-blue-500" />;
    }
    return <FileText className="w-4 h-4 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-20" />
        <Skeleton className="h-20" />
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (proofs.length === 0) {
    return (
      <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
        <FileText className="w-12 h-12 text-gray-300 mx-auto mb-2" />
        <p className="text-gray-600">Nenhum comprovante enviado</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="bg-blue-50 rounded-lg p-3 text-center border border-blue-200">
          <p className="text-2xl font-bold text-blue-600">{proofs.length}</p>
          <p className="text-xs text-blue-600">Total</p>
        </div>
        <div className="bg-amber-50 rounded-lg p-3 text-center border border-amber-200">
          <p className="text-2xl font-bold text-amber-600">
            {proofs.filter(p => p.is_duplicate).length}
          </p>
          <p className="text-xs text-amber-600">Duplicados</p>
        </div>
      </div>

      {/* List */}
      <div className="space-y-2">
        {proofs.map(proof => (
          <div
            key={proof.id}
            className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition"
          >
            {/* Info */}
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {getFileIcon(proof.file_type)}
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {proof.filename}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(proof.file_size)} • {formatDate(proof.uploaded_at)}
                </p>
                
                {/* 🌟 Valor extraído */}
                {(proof.extraction_status === 'EXTRACTED' || proof.extraction_status === 'EXTRACTED_WITH_ERROR') && proof.extracted_value && (
                  <p className="text-sm font-bold text-green-600 mt-1">
                    R$ {proof.extracted_value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                )}
              </div>
            </div>

            {/* Status e Ações */}
            <div className="flex items-center gap-2 ml-2">
              {proof.is_duplicate && (
                <Badge variant="warning">
                  <AlertCircle className="w-3 h-3 mr-1" />
                  Dup.
                </Badge>
              )}

              {/* 🌟 NOVO: Botão de Depósito */}
              {(proof.extraction_status === 'EXTRACTED' || proof.extraction_status === 'EXTRACTED_WITH_ERROR') && proof.extracted_value && !proof.deposited && (
                <Button
                  variant="success"
                  size="sm"
                  onClick={() => handleDeposit(proof.id, proof.extracted_value)}
                  disabled={depositing === proof.id}
                  className="flex items-center gap-1"
                >
                  {depositing === proof.id ? (
                    <>Depositando...</>
                  ) : (
                    <>
                      <DollarSign className="w-4 h-4" />
                      Depositar
                    </>
                  )}
                </Button>
              )}

              {/* ✓ Depositado */}
              {proof.deposited && (
                <Badge variant="success">
                  <Check className="w-3 h-3 mr-1" />
                  Depositado
                </Badge>
              )}

              {/* Delete */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDelete(proof.id)}
                className="text-red-500 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProofGallery;
