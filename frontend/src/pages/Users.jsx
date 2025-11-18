import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { UserPlus, Edit2, Trash2, Shield, ShieldOff, UserCheck, UserX } from 'lucide-react';
import { getUsers, createUser, updateUser, deleteUser } from '../services/api';

function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    is_admin: false
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await getUsers();
      setUsers(response.data.users);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
      toast.error('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.email || !formData.password) {
      toast.error('Preencha todos os campos obrigatórios');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Senha deve ter no mínimo 6 caracteres');
      return;
    }

    try {
      await createUser(
        formData.username,
        formData.email,
        formData.password,
        formData.full_name,
        formData.is_admin
      );
      
      toast.success('Usuário criado com sucesso!');
      setShowCreateModal(false);
      setFormData({ username: '', email: '', password: '', full_name: '', is_admin: false });
      loadUsers();
    } catch (error) {
      console.error('Erro ao criar usuário:', error);
      toast.error(error.response?.data?.detail || 'Erro ao criar usuário');
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      await updateUser(userId, { is_active: !currentStatus });
      toast.success(`Usuário ${!currentStatus ? 'ativado' : 'desativado'} com sucesso!`);
      loadUsers();
    } catch (error) {
      console.error('Erro ao atualizar usuário:', error);
      toast.error(error.response?.data?.detail || 'Erro ao atualizar usuário');
    }
  };

  const handleToggleAdmin = async (userId, currentStatus) => {
    try {
      await updateUser(userId, { is_admin: !currentStatus });
      toast.success(`Permissões de admin ${!currentStatus ? 'concedidas' : 'removidas'}!`);
      loadUsers();
    } catch (error) {
      console.error('Erro ao atualizar usuário:', error);
      toast.error(error.response?.data?.detail || 'Erro ao atualizar usuário');
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!confirm(`Tem certeza que deseja deletar o usuário "${username}"?`)) {
      return;
    }

    try {
      await deleteUser(userId);
      toast.success('Usuário deletado com sucesso!');
      loadUsers();
    } catch (error) {
      console.error('Erro ao deletar usuário:', error);
      toast.error(error.response?.data?.detail || 'Erro ao deletar usuário');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Carregando usuários...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Gerenciar Usuários</h1>
          <p className="text-slate-600 mt-1">Controle de acesso ao sistema</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
        >
          <UserPlus className="h-5 w-5" />
          Novo Usuário
        </button>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Usuário</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Email</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Nome</th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-slate-700">Status</th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-slate-700">Admin</th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-slate-700">Último Login</th>
              <th className="px-6 py-4 text-center text-sm font-semibold text-slate-700">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <span className="font-medium text-slate-900">{user.username}</span>
                </td>
                <td className="px-6 py-4 text-slate-600">{user.email}</td>
                <td className="px-6 py-4 text-slate-600">{user.full_name || '-'}</td>
                <td className="px-6 py-4 text-center">
                  <button
                    onClick={() => handleToggleActive(user.id, user.is_active)}
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                      user.is_active
                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                        : 'bg-red-100 text-red-700 hover:bg-red-200'
                    }`}
                  >
                    {user.is_active ? <UserCheck className="h-3 w-3" /> : <UserX className="h-3 w-3" />}
                    {user.is_active ? 'Ativo' : 'Inativo'}
                  </button>
                </td>
                <td className="px-6 py-4 text-center">
                  <button
                    onClick={() => handleToggleAdmin(user.id, user.is_admin)}
                    className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                      user.is_admin
                        ? 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {user.is_admin ? <Shield className="h-3 w-3" /> : <ShieldOff className="h-3 w-3" />}
                    {user.is_admin ? 'Admin' : 'Usuário'}
                  </button>
                </td>
                <td className="px-6 py-4 text-center text-sm text-slate-600">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString('pt-BR') : 'Nunca'}
                </td>
                <td className="px-6 py-4 text-center">
                  <button
                    onClick={() => handleDeleteUser(user.id, user.username)}
                    className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                    title="Deletar usuário"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Criar Novo Usuário</h2>
            
            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Username *
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="email@exemplo.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Senha * (mínimo 6 caracteres)
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="••••••"
                  required
                  minLength={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Nome Completo
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Nome completo"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_admin"
                  checked={formData.is_admin}
                  onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                  className="w-4 h-4 text-green-600 border-slate-300 rounded focus:ring-green-500"
                />
                <label htmlFor="is_admin" className="text-sm font-medium text-slate-700">
                  Conceder permissões de administrador
                </label>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setFormData({ username: '', email: '', password: '', full_name: '', is_admin: false });
                  }}
                  className="flex-1 px-4 py-3 border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-all"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-3 rounded-lg font-medium hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg"
                >
                  Criar Usuário
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Users;
