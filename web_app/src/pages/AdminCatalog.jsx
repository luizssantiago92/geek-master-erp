import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { Settings, Save, CheckCircle, Clock, AlertTriangle, Send } from 'lucide-react';

export default function AdminCatalog() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState([]);
  const [session, setSession] = useState(null);
  const [authError, setAuthError] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Verifica Autenticação Mágica
  useEffect(() => {
    checkMagicLink();
  }, []);

  async function checkMagicLink() {
    try {
      const token = searchParams.get('token');
      
      if (token) {
        setLoading(true);
        // Validar Token no banco
        const { data, error } = await supabase
          .from('sessoes_magicas')
          .select('*')
          .eq('token', token)
          .single();

        if (error || !data) {
          setAuthError('Token inválido ou não encontrado.');
        } else if (data.usado) {
          setAuthError('Este link já foi utilizado. Gere um novo no Bot.');
        } else {
          // Token válido, "queimar" o token e salvar sessão
          await supabase.from('sessoes_magicas').update({ usado: true }).eq('token', token);
          
          const sessionData = {
            telegram_id: data.telegram_id,
            nivel_acesso: data.nivel_acesso,
            expires: new Date().getTime() + 1000 * 60 * 60 * 24 // 24 horas
          };
          localStorage.setItem('adminSession', JSON.stringify(sessionData));
          setSession(sessionData);
          
          // Limpa a URL
          navigate('/admin', { replace: true });
        }
      } else {
        // Sem token na URL, verificar localStorage
        const cached = localStorage.getItem('adminSession');
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed.expires > new Date().getTime()) {
            setSession(parsed);
          } else {
            localStorage.removeItem('adminSession');
            setAuthError('Sua sessão expirou. Gere um novo link no Bot.');
          }
        } else {
          setAuthError('Acesso Restrito. Por favor, solicite um Link de Acesso através do Bot no Telegram.');
        }
      }
    } catch (err) {
      setAuthError('Erro na autenticação.');
    } finally {
      if (!authError) {
        fetchProdutos();
      } else {
        setLoading(false);
      }
    }
  }

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

  // Mudar status para PUBLICADO (Admin) ou Solicitar Publicação (Outros)
  const handlePublish = async (produto) => {
    if (!session) return;
    
    try {
      if (session.nivel_acesso >= 4) {
        // ADMIN PUBLICA DIRETO
        const novoStatus = produto.status_publicacao === 'PUBLICADO' ? 'PENDENTE' : 'PUBLICADO';
        const { error } = await supabase
          .from('produtos')
          .update({ status_publicacao: novoStatus })
          .eq('id', produto.id);

        if (error) throw error;
        
        setProdutos(prev => prev.map(p => p.id === produto.id ? { ...p, status_publicacao: novoStatus } : p));
        if (novoStatus === 'PUBLICADO') {
          alert('Produto ENVIADO para o site principal com sucesso!');
        } else {
          alert('Produto RECOLHIDO do site (agora está Pendente).');
        }
      } else {
        // GESTORES/MARKETING: Apenas solicitam
        if (produto.status_publicacao === 'AGUARDANDO_APROVACAO') {
          alert('Este produto já está aguardando aprovação do Admin.');
          return;
        }

        const { error } = await supabase
          .from('produtos')
          .update({ status_publicacao: 'AGUARDANDO_APROVACAO' })
          .eq('id', produto.id);

        if (error) throw error;

        // Inserir notificação para o Bot
        await supabase.from('notificacoes_bot').insert({
          mensagem: `Um gestor solicitou a publicação do produto *${produto.nome}* no painel web. Acesse para conferir e aprovar.`,
          lido: false
        });

        setProdutos(prev => prev.map(p => p.id === produto.id ? { ...p, status_publicacao: 'AGUARDANDO_APROVACAO' } : p));
        alert('Solicitação de publicação enviada ao Administrador!');
      }
    } catch (err) {
      console.error(err);
      alert('Erro ao processar publicação.');
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

  if (authError) {
    return (
      <div className="container mx-auto px-4 py-20 max-w-2xl text-center">
        <div className="bg-red-50 text-red-600 p-8 rounded-xl border-2 border-red-200">
          <AlertTriangle size={64} className="mx-auto mb-4" />
          <h2 className="text-2xl font-black mb-2">Acesso Restrito</h2>
          <p className="font-medium">{authError}</p>
        </div>
      </div>
    );
  }

  if (loading || !session) return <div className="p-8 text-center text-gray-500 animate-pulse font-bold">Autenticando & Carregando Catálogo Seguro...</div>;

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
              
              {session?.nivel_acesso >= 4 ? (
                <button 
                  onClick={() => handlePublish(p)}
                  className={`w-full text-white font-bold py-3 px-4 rounded flex items-center justify-center gap-2 transition-colors shadow-sm ${p.status_publicacao === 'PUBLICADO' ? 'bg-red-500 hover:bg-red-600' : 'bg-primary hover:bg-orange-600'}`}
                >
                  {p.status_publicacao === 'PUBLICADO' ? 'Ocultar do Site' : 'Enviar para o Site'}
                </button>
              ) : (
                <button 
                  onClick={() => handlePublish(p)}
                  disabled={p.status_publicacao === 'PUBLICADO' || p.status_publicacao === 'AGUARDANDO_APROVACAO'}
                  className={`w-full text-white font-bold py-3 px-4 rounded flex items-center justify-center gap-2 transition-colors shadow-sm ${p.status_publicacao === 'PUBLICADO' || p.status_publicacao === 'AGUARDANDO_APROVACAO' ? 'bg-gray-400 cursor-not-allowed' : 'bg-yellow-500 hover:bg-yellow-600'}`}
                >
                  <Send size={16} /> {p.status_publicacao === 'AGUARDANDO_APROVACAO' ? 'Aprovação Pendente' : (p.status_publicacao === 'PUBLICADO' ? 'Publicado' : 'Solicitar Publicação')}
                </button>
              )}
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
