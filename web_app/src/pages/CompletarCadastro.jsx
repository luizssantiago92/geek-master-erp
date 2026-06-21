import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { supabase } from '../lib/supabase';

export default function CompletarCadastro() {
  const navigate = useNavigate();
  const { completeRegistration, updateUser } = useUser();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    cpf: '',
    dataNascimento: '',
    telefone: '',
    isWhatsapp: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Tenta buscar cliente existente pelo CPF
      let clienteId = null;
      const { data: existente } = await supabase.from('clientes').select('id').eq('cpf', formData.cpf).single();
      
      if (existente) {
        clienteId = existente.id;
        // Atualiza os dados
        await supabase.from('clientes').update({
          nome: formData.nome,
          telefone: formData.telefone
        }).eq('id', clienteId);
      } else {
        // 2. Se não existir, cria um novo
        const { data: novoCliente, error } = await supabase.from('clientes').insert({
          cpf: formData.cpf,
          nome: formData.nome,
          telefone: formData.telefone,
          nivel_vip: 'Novato'
        }).select().single();
        
        if (error) throw error;
        clienteId = novoCliente.id;
      }

      // Salva no contexto
      updateUser({
        ...formData,
        cliente_id: clienteId
      });

      completeRegistration();
      alert('Dados salvos com sucesso!');
      navigate({ pathname: '/onboarding', search: window.location.search });
    } catch (error) {
      console.error('Erro ao salvar cliente:', error);
      alert('Ocorreu um erro ao salvar seus dados. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate({ pathname: '/onboarding', search: window.location.search });
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-2xl">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-black text-dark mb-2">Completar Cadastro</h1>
          <p className="text-gray-500">
            Falta pouco! Precisamos apenas de mais algumas informações para podermos processar suas encomendas e retiradas nos quiosques Piticas Rio.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nome Completo */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Nome Completo</label>
            <input 
              type="text" 
              required
              placeholder="Digite seu nome completo"
              value={formData.nome}
              onChange={e => setFormData({...formData, nome: e.target.value})}
              className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* E-mail */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">E-mail</label>
              <input 
                type="email" 
                required
                placeholder="seu@email.com"
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>
            {/* CPF */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">CPF (Necessário para retirada)</label>
              <input 
                type="text" 
                required
                placeholder="000.000.000-00"
                value={formData.cpf}
                onChange={e => setFormData({...formData, cpf: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Data de Nascimento */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Data de Nascimento</label>
              <input 
                type="date" 
                required
                value={formData.dataNascimento}
                onChange={e => setFormData({...formData, dataNascimento: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>
            {/* Telefone */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Número de Telefone</label>
              <input 
                type="text" 
                required
                placeholder="(00) 00000-0000"
                value={formData.telefone}
                onChange={e => setFormData({...formData, telefone: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>
          </div>

          {/* Checkbox WhatsApp */}
          <div className="flex items-center gap-2 pt-2">
            <input 
              type="checkbox" 
              id="isWhatsapp"
              checked={formData.isWhatsapp}
              onChange={e => setFormData({...formData, isWhatsapp: e.target.checked})}
              className="w-5 h-5 text-primary border-gray-300 rounded focus:ring-primary"
            />
            <label htmlFor="isWhatsapp" className="text-sm font-medium text-gray-700 cursor-pointer">
              Este número de telefone também é meu WhatsApp
            </label>
          </div>

          {/* Submit */}
          <div className="pt-6 border-t border-gray-100 flex flex-col gap-3">
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-primary hover:bg-orange-600 disabled:opacity-50 text-light font-bold py-3 rounded transition-colors text-lg"
            >
              {loading ? 'Salvando...' : 'Continuar e Salvar'}
            </button>
            <button 
              type="button" 
              onClick={handleSkip}
              className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-3 rounded transition-colors text-lg"
            >
              Pular por enquanto
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
