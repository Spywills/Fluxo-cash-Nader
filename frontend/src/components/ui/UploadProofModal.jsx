import React, { useState } from 'react';
import { X, Upload } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';
import { FileUpload } from './FileUpload';
import { ProofGallery } from './ProofGallery';
import { uploadProof } from '../../services/api';
import showToast from '../../utils/toast';

/**
 * UploadProofModal - Modal para upload de comprovantes do cliente
 * @param {string} clientId - ID do cliente
 * @param {string} clientName - Nome do cliente
 * @param {boolean} isOpen - Estado do modal
 * @param {function} onClose - Callback ao fechar
 * @param {function} onSuccess - Callback ao sucesso
 * @param {function} onBalanceUpdate - Callback ao depositar (atualiza saldo)
 */
export const UploadProofModal = ({
  clientId,
  clientName,
  isOpen,
  onClose,
  onSuccess = () => {},
  onBalanceUpdate = () => {},
}) => {
  const [tab, setTab] = useState('upload'); // upload | gallery
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUpload = async (file) => {
    // Proteger contra clientId undefined
    if (!clientId || clientId === 'undefined') {
      showToast.error(
        'Erro ao Enviar',
        'Erro: Cliente não identificado. Recarregue a página.'
      );
      console.warn('handleUpload - clientId é undefined:', clientId);
      return;
    }

    try {
      const response = await uploadProof(clientId, file);
      
      if (response.data.is_duplicate) {
        showToast.warning(
          'Arquivo Duplicado',
          `Este comprovante já foi enviado anteriormente`
        );
      } else {
        showToast.success(
          'Comprovante Enviado',
          `${file.name} adicionado com sucesso`
        );
      }

      // Refresh gallery
      setRefreshKey(prev => prev + 1);
      onSuccess?.();
      
      return response.data;
    } catch (error) {
      showToast.error(
        'Erro ao Enviar',
        error.response?.data?.detail || 'Tente novamente'
      );
      throw error;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Comprovantes - ${clientName}`}
      size="lg"
    >
      <div className="space-y-4">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200">
          <button
            onClick={() => setTab('upload')}
            className={`px-4 py-2 font-medium text-sm transition border-b-2 ${
              tab === 'upload'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Upload className="w-4 h-4 inline mr-2" />
            Enviar
          </button>
          <button
            onClick={() => setTab('gallery')}
            className={`px-4 py-2 font-medium text-sm transition border-b-2 ${
              tab === 'gallery'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Arquivos
          </button>
        </div>

        {/* Content */}
        {tab === 'upload' && (
          <FileUpload
            accept=".pdf,.png,.jpg,.jpeg"
            maxSize={10}
            onUpload={handleUpload}
            label="Enviar Comprovante"
            description="PDF ou PNG (máx 10MB). Arquivos duplicados são detectados automaticamente."
          />
        )}

        {tab === 'gallery' && (
          <ProofGallery
            key={refreshKey}
            clientId={clientId}
            onRefresh={() => setRefreshKey(prev => prev + 1)}
            onBalanceUpdate={onBalanceUpdate}
          />
        )}
      </div>
    </Modal>
  );
};

export default UploadProofModal;
