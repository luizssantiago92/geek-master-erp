import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Settings, Save, CheckCircle, Clock } from 'lucide-react';

export default function AdminCatalog() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState([]);

  // Busca inicial dos produtos
  useEffect(() => {
    fetchProdutos();
  }, []);

  async function fetchProdutos() {
    setLoading(true);
    const { data } = await supabase
      .from('produtos')
      .select('*')
      .order('criado_em', { ascending: false });
    
    if (data) {
      setProdutos(data);
    }
    setLoading(false);
  }

  // Atualiza campo localmente antes de salvar
  const handleChange = (id, field, value) => {
    setProdutos(prev => prev.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  // Salvar edições do produto no banco
  const handleSave = async (produto) => {
    try {
      const { error } = await supabase
        .from('produtos')
        .update({
          nome: produto.nome,
          preco_base: produto.preco_base,
          descricao: produto.descricao,
          is_new: produto.is_new
        })
        .eq('id', produto.id);

      if (error) throw error;
      alert(`Produto "${produto.nome}" salvo com sucesso!`);
    } catch (err) {
      console.error(err);
      alert('Erro ao salvar produto.');
    }
  };

  // Mudar status para PUBLICADO (enviar para o site)
  const handlePublish = async (produto) => {
    try {
      const novoStatus = produto.status_publicacao === 'PUBLICADO' ? 'PENDENTE' : 'PUBLICADO';
      const { error } = await supabase
        .from('produtos')
        .update({ status_publicacao: novoStatus })
        .eq('id', produto.id);

      if (error) throw error;
      
      // Atualiza o estado local
      setProdutos(prev => prev.map(p => p.id === produto.id ? { ...p, status_publicacao: novoStatus } : p));
      
      if (novoStatus === 'PUBLICADO') {
        alert('Produto ENVIADO para o site principal com sucesso!');
      } else {
        alert('Produto RECOLHIDO do site (agora está Pendente).');
      }
    } catch (err) {
      console.error(err);
      alert('Erro ao mudar status do produto.');
    }
  };

  // Ações em Massa
  const toggleSelection = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const selectAll = () => {
    if (selectedIds.length === produtos.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(produtos.map(p => p.id));
    }
  };

  const handleBulkSave = async () => {
    if (selectedIds.length === 0) return;
    try {
      // Como cada produto tem valores diferentes, precisamos fazer updates individuais
      const selectedProducts = produtos.filter(p => selectedIds.includes(p.id));
      const promises = selectedProducts.map(p => 
        supabase.from('produtos').update({
          nome: p.nome,
          preco_base: p.preco_base,
          descricao: p.descricao,
          is_new: p.is_new
        }).eq('id', p.id)
      );
      
      await Promise.all(promises);
      alert(`${selectedIds.length} produtos salvos com sucesso!`);
      setSelectedIds([]);
    } catch (err) {
      console.error(err);
      alert('Erro ao salvar produtos em massa.');
    }
  };

  const handleBulkPublish = async () => {
    if (selectedIds.length === 0) return;
    try {
      const { error } = await supabase
        .from('produtos')
        .update({ status_publicacao: 'PUBLICADO' })
        .in('id', selectedIds);

      if (error) throw error;
      
      setProdutos(prev => prev.map(p => selectedIds.includes(p.id) ? { ...p, status_publicacao: 'PUBLICADO' } : p));
      alert(`${selectedIds.length} produtos ENVIADOS para o site com sucesso!`);
      setSelectedIds([]);
    } catch (err) {
      console.error(err);
      alert('Erro ao publicar produtos em massa.');
    }
  };

  if (loading) return <div className="p-8 text-center">Carregando catálogo admin...</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="flex items-center gap-3 mb-8">
        <Settings size={32} className="text-primary" />
        <h1 className="text-3xl font-black text-dark uppercase tracking-widest">Painel Administrativo: Catálogo</h1>
      </div>
      
      <p className="text-gray-600 mb-8">
        Aqui você gerencia os produtos cadastrados pelo Robô. Eles entram como <span className="font-bold text-yellow-600">PENDENTE</span> e não aparecem no site até que você revise os dados e clique em "Publicar no Site".
      </p>

      {/* Barra de Ações em Massa */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4 sticky top-4 z-10">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer font-bold text-dark">
            <input 
              type="checkbox" 
              checked={selectedIds.length === produtos.length && produtos.length > 0}
              onChange={selectAll}
              className="w-5 h-5 text-primary rounded"
            />
            Selecionar Todos ({selectedIds.length} selecionados)
          </label>
        </div>
        
        {selectedIds.length > 0 && (
          <div className="flex gap-3">
            <button 
              onClick={handleBulkSave}
              className="bg-gray-100 hover:bg-gray-200 text-dark font-bold py-2 px-4 rounded flex items-center gap-2 transition-colors text-sm shadow-sm border border-gray-300"
            >
              <Save size={16} /> Salvar Selecionados
            </button>
            <button 
              onClick={handleBulkPublish}
              className="bg-primary hover:bg-orange-600 text-white font-bold py-2 px-4 rounded flex items-center gap-2 transition-colors shadow-sm"
            >
              <CheckCircle size={16} /> Enviar Selecionados para Site
            </button>
          </div>
        )}
      </div>

      <div className="grid gap-6">
        {produtos.map(p => (
          <div key={p.id} className={`bg-white rounded-xl border-2 shadow-sm p-6 flex flex-col md:flex-row gap-6 relative transition-all ${selectedIds.includes(p.id) ? 'ring-2 ring-primary border-primary' : (p.status_publicacao === 'PUBLICADO' ? 'border-green-400' : 'border-yellow-400')}`}>
            
            {/* Checkbox Individual */}
            <div className="absolute top-4 left-4 z-10">
              <input 
                type="checkbox"
                checked={selectedIds.includes(p.id)}
                onChange={() => toggleSelection(p.id)}
                className="w-6 h-6 text-primary rounded cursor-pointer border-2 border-gray-300 focus:ring-primary"
              />
            </div>

            {/* Foto e Status */}
            <div className="w-full md:w-48 flex flex-col items-center gap-3">
              <div className="w-32 h-32 bg-gray-100 rounded-lg overflow-hidden border border-gray-200">
                {p.imagem_url ? (
                  <img src={p.imagem_url} alt="Produto" className="w-full h-full object-contain" onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/400x400/eeeeee/999999?text=Sem+Foto" }} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-xs text-gray-400">Sem Foto</div>
                )}
              </div>
              <div className={`flex items-center gap-1 font-bold text-sm px-3 py-1 rounded-full ${p.status_publicacao === 'PUBLICADO' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                {p.status_publicacao === 'PUBLICADO' ? <CheckCircle size={16} /> : <Clock size={16} />}
                {p.status_publicacao || 'PENDENTE'}
              </div>
            </div>

            {/* Formulário de Edição */}
            <div className="flex-1 space-y-4">
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Nome do Produto</label>
                <input 
                  type="text" 
                  value={p.nome || ''} 
                  onChange={(e) => handleChange(p.id, 'nome', e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:outline-none font-bold text-dark"
                />
              </div>
              
              <div className="flex gap-4">
                <div className="w-1/3">
                  <label className="text-xs font-bold text-gray-500 uppercase">Preço Base (R$)</label>
                  <input 
                    type="number" 
                    step="0.01"
                    value={p.preco_base || 0} 
                    onChange={(e) => handleChange(p.id, 'preco_base', parseFloat(e.target.value))}
                    className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                  />
                </div>
                <div className="flex items-center pt-5">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={p.is_new || false}
                      onChange={(e) => handleChange(p.id, 'is_new', e.target.checked)}
                      className="w-5 h-5 text-primary rounded"
                    />
                    <span className="text-sm font-bold text-gray-700">É Lançamento?</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Descrição / Info Técnica</label>
                <textarea 
                  value={p.descricao || ''} 
                  onChange={(e) => handleChange(p.id, 'descricao', e.target.value)}
                  rows={2}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:outline-none text-sm"
                />
              </div>
            </div>

            {/* Ações */}
            <div className="w-full md:w-48 flex flex-col justify-end gap-3 border-t md:border-t-0 md:border-l border-gray-100 pt-4 md:pt-0 md:pl-6">
              <button 
                onClick={() => handleSave(p)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-dark font-bold py-2 px-4 rounded flex items-center justify-center gap-2 transition-colors text-sm"
              >
                <Save size={16} /> Salvar Edição
              </button>
              
              <button 
                onClick={() => handlePublish(p)}
                className={`w-full text-white font-bold py-3 px-4 rounded flex items-center justify-center gap-2 transition-colors shadow-sm ${p.status_publicacao === 'PUBLICADO' ? 'bg-red-500 hover:bg-red-600' : 'bg-primary hover:bg-orange-600'}`}
              >
                {p.status_publicacao === 'PUBLICADO' ? 'Ocultar do Site' : 'Enviar para o Site'}
              </button>
            </div>

          </div>
        ))}

        {produtos.length === 0 && (
          <div className="text-center py-12 text-gray-500">Nenhum produto cadastrado no banco de dados.</div>
        )}
      </div>
    </div>
  );
}
