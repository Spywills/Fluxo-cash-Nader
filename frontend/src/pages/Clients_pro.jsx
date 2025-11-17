import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Edit2, Search, Phone, Mail, IdCard, Upload, Users } from 'lucide-react';
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { SkeletonCard } from '../components/ui/Skeleton';
import { UploadProofModal } from '../components/ui/UploadProofModal';
import { getClients, createClient, deleteClient, updateClientNotes } from '../services/api';
import showToast from '../utils/toast';

export default function Clients() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingNotesId, setEditingNotesId] = useState(null);
  const [editingNotes, setEditingNotes] = useState({});
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    notes: '',
  });

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await getClients();
      // backend may return { clients: [...] } or an array directly
      setClients(response.data?.clients ?? response.data ?? []);
      setError(null);
    } catch (err) {
      setError(err.message);
      showToast.error('Erro', 'Não conseguimos carregar os clientes');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClient = async (e) => {
    e.preventDefault();
    try {
      await createClient(formData);
      setFormData({ name: '', notes: '' });
      setIsModalOpen(false);
      showToast.success('Sucesso', 'Cliente criado com sucesso!');
      loadClients();
    } catch (err) {
      showToast.error('Erro', err.message);
    }
  };

  const handleDeleteClient = async (id) => {
    if (confirm('Tem certeza que deseja deletar este cliente?')) {
      try {
        await deleteClient(id);
        showToast.success('Sucesso', 'Cliente deletado');
        loadClients();
      } catch (err) {
        showToast.error('Erro', err.message);
      }
    }
  };

  const handleSaveNotes = async (clientId) => {
    // Proteger contra clientId undefined
    if (!clientId || clientId === 'undefined') {
      showToast.error('Erro', 'Cliente não identificado');
      console.warn('handleSaveNotes - clientId é undefined:', clientId);
      return;
    }

    try {
      await updateClientNotes(clientId, editingNotes[clientId]);
      setEditingNotesId(null);
      showToast.success('Sucesso', 'Notas atualizadas');
      loadClients();
    } catch (err) {
      showToast.error('Erro', err.message);
    }
  };

  // Defensivo: garantir que clients é um array
  const safeClients = Array.isArray(clients) ? clients : [];

  const filteredClients = safeClients.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.document && c.document.includes(searchTerm))
  );

  const formatMoney = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  if (loading && clients.length === 0) return <div className="container mx-auto px-4 py-8"><SkeletonCard /></div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Clientes</h1>
          <p className="text-gray-600">Gerencie todos os seus clientes</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} variant="primary" size="lg">
          <Plus className="h-5 w-5" />
          Novo Cliente
        </Button>
      </div>

      {error && (
        <Alert variant="danger" title="Erro" description={error} className="mb-6" />
      )}

      {/* Search */}
      <div className="mb-6">
        <Input
          placeholder="Buscar por nome, email ou documento..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          icon={Search}
          size="lg"
        />
      </div>

      {/* Grid de Clientes */}
      {filteredClients.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredClients.map(client => (
            <Card key={client.id} className="hover:shadow-lg transition-shadow">
              <CardBody className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900">{client.name}</h3>
                    {client.saldo_atual !== undefined && (
                      <p className={`text-2xl font-bold mt-2 ${
                        client.saldo_atual >= 0 ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {formatMoney(client.saldo_atual)}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedClient(client);
                        setUploadModalOpen(true);
                      }}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Upload de comprovantes"
                    >
                      <Upload className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteClient(client.id)}
                      className="p-2 text-danger-600 hover:bg-danger-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Info */}
                <div className="space-y-2 text-sm">
                  {client.email && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <Mail className="h-4 w-4" />
                      {client.email}
                    </div>
                  )}
                  {client.phone && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <Phone className="h-4 w-4" />
                      {client.phone}
                    </div>
                  )}
                  {client.document && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <IdCard className="h-4 w-4" />
                      {client.document}
                    </div>
                  )}
                </div>

                {/* Status */}
                <div>
                  {client.saldo_atual !== undefined && (
                    <Badge variant={client.saldo_atual >= 0 ? 'success' : 'danger'} size="md">
                      {client.saldo_atual >= 0 ? '✓ Positivo' : '✕ Negativo'}
                    </Badge>
                  )}
                </div>

                {/* Notes */}
                {editingNotesId === client.id ? (
                  <div className="space-y-2">
                    <textarea
                      value={editingNotes[client.id] || ''}
                      onChange={(e) => setEditingNotes({ ...editingNotes, [client.id]: e.target.value })}
                      placeholder="Anotações..."
                      className="w-full p-2 border rounded-lg text-sm"
                      rows="3"
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="success"
                        onClick={() => handleSaveNotes(client.id)}
                        className="flex-1"
                      >
                        Salvar
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setEditingNotesId(null)}
                        className="flex-1"
                      >
                        Cancelar
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div
                    onClick={() => {
                      setEditingNotesId(client.id);
                      setEditingNotes({ ...editingNotes, [client.id]: client.notes || '' });
                    }}
                    className="cursor-pointer p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Edit2 className="h-4 w-4 text-gray-500" />
                      <span className="text-xs font-semibold text-gray-600">ANOTAÇÕES</span>
                    </div>
                    <p className="text-sm text-gray-700">
                      {client.notes || '(Clique para adicionar anotações)'}
                    </p>
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="text-center py-12">
          <CardBody>
            <Users className="h-12 w-12 mx-auto mb-4 opacity-30" />
            <p className="text-gray-600">Nenhum cliente encontrado</p>
          </CardBody>
        </Card>
      )}

      {/* Modal Novo Cliente */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Novo Cliente">
        <form onSubmit={handleCreateClient} className="space-y-4">
          <Input
            label="Nome do Cliente *"
            placeholder="Ex: João Silva"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            autoFocus
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Anotações</label>
            <textarea
              placeholder="Anotações sobre o cliente..."
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              rows="3"
            />
          </div>
          <div className="flex gap-2 pt-4">
            <Button type="submit" variant="primary" className="flex-1">
              Criar Cliente
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="flex-1"
              onClick={() => setIsModalOpen(false)}
            >
              Cancelar
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal Upload de Comprovantes */}
      {selectedClient && (
        <UploadProofModal
          clientId={selectedClient.id}
          clientName={selectedClient.name}
          isOpen={uploadModalOpen}
          onClose={() => {
            setUploadModalOpen(false);
            setSelectedClient(null);
          }}
          onSuccess={() => {
            // Refresh clientes se necessário
          }}
        />
      )}
    </div>
  );
}
