import React, { useState } from 'react';
import { MapPin, Info, ArrowLeft, X } from 'lucide-react';
import { useCart } from '../contexts/CartContext';
import { useUser } from '../contexts/UserContext';
import { useNavigate, Link } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import ProductCard from '../components/ProductCard';

const KIOSKS = [
  {
    id: 'metropolitano',
    name: 'Quiosque Shopping Metropolitano',
    address: 'Av. Embaixador Abelardo Bueno, 1300 - Barra da Tijuca, RJ, 22775-040',
    complement: 'Quiosque 1º Piso',
    mapQuery: 'Shopping Metropolitano Barra, Rio de Janeiro'
  },
  {
    id: 'taquara',
    name: 'Quiosque Taquara Plaza Shopping',
    address: 'Estr. Rodrigues Caldas, 127 - Taquara, RJ, 22713-372',
    complement: 'Quiosque 2º Piso',
    mapQuery: 'Taquara Plaza Shopping, Rio de Janeiro'
  },
  {
    id: 'americas',
    name: 'Quiosque Americas Shopping',
    address: 'Av. das Américas, 15500 - Recreio dos Bandeirantes, RJ, 22790-702',
    complement: 'Quiosque 1º Piso',
    mapQuery: 'Americas Shopping, Recreio dos Bandeirantes'
  },
  {
    id: 'boulevard',
    name: 'Quiosque Shopping Boulevard',
    address: 'R. Barão de São Francisco, 236 - Vila Isabel, RJ, 20560-030',
    complement: 'Quiosque 1º Piso',
    mapQuery: 'Shopping Boulevard, Vila Isabel, Rio de Janeiro'
  },
  {
    id: 'novaamerica',
    name: 'Quiosque Shopping Nova América',
    address: 'Av. Pastor Martin Luther King Jr., 126 - Del Castilho, RJ, 20765-000',
    complement: 'Quiosque 1º Piso',
    mapQuery: 'Shopping Nova América, Del Castilho, Rio de Janeiro'
  }
];

export default function Checkout() {
  const { cart, totalPrice, clearCart } = useCart();
  const { user, isRegistrationComplete } = useUser();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    kiosk: 'metropolitano',
    cupom: ''
  });
  
  const [recommendations, setRecommendations] = useState([]);

  React.useEffect(() => {
    async function fetchRecs() {
      // Busca alguns produtos aleatórios (ou baseados na franquia) para recomendar
      const { data } = await supabase.from('produtos').select('*').limit(8);
      if (data) {
        const recs = data.map(item => ({
            id: item.id,
            title: item.nome.replace('[TESTE]', '').trim(),
            franchise: item.franquia || 'Geral',
            price: item.preco_base || 0,
            isNew: item.nome.includes('[TESTE]'), 
            image: item.imagem_url || "https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&q=80&w=400"
        })).sort(() => 0.5 - Math.random()).slice(0, 4); // Pega 4 aleatórios
        setRecommendations(recs);
      }
    }
    fetchRecs();
  }, []);

  if (cart.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-4">Sua encomenda está vazia</h2>
        <button onClick={() => navigate('/')} className="text-primary hover:underline">Voltar ao catálogo</button>
      </div>
    );
  }

  const handleFinish = async (e) => {
    e.preventDefault();
    if (!user || !user.cliente_id) {
      alert("Por favor, complete seu cadastro antes de finalizar a encomenda.");
      navigate('/completar-cadastro');
      return;
    }
    
    try {
      // 1. Gera código de retirada (ex: A8F2)
      const codigoRetirada = Math.random().toString(36).substring(2, 6).toUpperCase();

      // Para fins de teste, como não temos quiosques reais no banco com ID, passamos null (ON DELETE SET NULL na tabela permite isso por enquanto)
      const { data: encomenda, error: encError } = await supabase.from('encomendas').insert({
        cliente_id: user.cliente_id,
        codigo_retirada: codigoRetirada,
        valor_original: totalPrice,
        status: 'PENDENTE'
      }).select().single();

      if (encError) throw encError;

      // 2. Insere os itens da encomenda
      const itemsToInsert = cart.map(item => ({
        encomenda_id: encomenda.id,
        produto_id: item.id,
        quantidade: item.quantity,
        preco_unitario: item.price
      }));

      const { error: itemsError } = await supabase.from('encomendas_items').insert(itemsToInsert);
      if (itemsError) throw itemsError;

      alert(`Encomenda realizada com sucesso! Código: ${codigoRetirada}. Em breve enviaremos detalhes no WhatsApp!`);
      clearCart();
      navigate('/conta');
    } catch (error) {
      console.error('Erro ao finalizar encomenda:', error);
      alert('Erro ao processar sua encomenda. Tente novamente.');
    }
  };

  const selectedKiosk = KIOSKS.find(k => k.id === formData.kiosk);

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <h1 className="text-3xl font-black text-dark mb-8">Finalizar Encomenda (Retirada)</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Form */}
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
          <h2 className="text-xl font-bold mb-6">Confirme seus dados para retirada</h2>
          <form onSubmit={handleFinish} className="space-y-4">
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Quiosque de Retirada</label>
              <select 
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none mb-4"
                value={formData.kiosk}
                onChange={e => setFormData({...formData, kiosk: e.target.value})}
              >
                {KIOSKS.map(kiosk => (
                  <option key={kiosk.id} value={kiosk.id}>{kiosk.name}</option>
                ))}
              </select>

              {/* Informações e Mapa do Quiosque Selecionado */}
              {selectedKiosk && (
                <div className="bg-gray-50 border border-gray-200 rounded p-4 mt-2">
                  <p className="text-sm font-bold text-dark mb-1">{selectedKiosk.name}</p>
                  <p className="text-xs text-gray-600 mb-1">{selectedKiosk.address}</p>
                  <p className="text-xs text-primary font-semibold mb-3">Complemento: {selectedKiosk.complement}</p>
                  
                  <div className="w-full h-72 bg-gray-200 rounded overflow-hidden">
                    <iframe
                      title={`Mapa para ${selectedKiosk.name}`}
                      width="100%"
                      height="100%"
                      style={{ border: 0 }}
                      loading="lazy"
                      allowFullScreen
                      src={`https://www.google.com/maps?q=${encodeURIComponent(selectedKiosk.mapQuery)}&output=embed`}
                    ></iframe>
                  </div>
                </div>
              )}
            </div>
          </form>
        </div>

        {/* Order Summary */}
        <div className="bg-gray-50 p-6 rounded-xl border border-gray-100 flex flex-col h-fit">
          <h2 className="text-xl font-bold mb-6">Resumo da Encomenda</h2>
          
          <div className="space-y-4 mb-6 flex-1 max-h-[400px] overflow-y-auto pr-2">
            {cart.map(item => (
              <div key={item.id} className="flex gap-4 items-center bg-white p-3 rounded shadow-sm border border-gray-100 relative group">
                <button 
                  onClick={() => removeFromCart(item.id)}
                  className="absolute -top-2 -right-2 bg-red-100 text-red-600 hover:bg-red-600 hover:text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-all shadow-sm"
                  title="Remover produto"
                >
                  <X size={14} />
                </button>
                <img src={item.image} alt={item.title} className="w-16 h-16 object-cover rounded" />
                <div className="flex-1">
                  <h3 className="font-semibold text-sm text-dark line-clamp-2">{item.title}</h3>
                  <p className="text-xs text-gray-500">Qtd: {item.quantity}</p>
                </div>
                <div className="font-bold text-dark whitespace-nowrap">
                  R$ {(item.price * item.quantity).toFixed(2).replace('.', ',')}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-200 pt-6">
            {/* Cupom de Desconto */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Cupom de Desconto</label>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  placeholder="Ex: GEEK10"
                  value={formData.cupom}
                  onChange={e => setFormData({...formData, cupom: e.target.value})}
                  className="flex-1 border border-gray-300 rounded px-3 py-2 focus:ring-2 focus:ring-primary focus:outline-none uppercase"
                />
                <button 
                  type="button" 
                  onClick={() => alert("Cupom aplicado! (Simulação)")}
                  className="bg-dark hover:bg-gray-800 text-light px-4 py-2 rounded font-semibold transition-colors"
                >
                  Aplicar
                </button>
              </div>
            </div>

            {/* Totais */}
            <div className="space-y-2 mb-6 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>R$ {totalPrice.toFixed(2).replace('.', ',')}</span>
              </div>
              <div className="flex justify-between text-green-600">
                <span>Desconto</span>
                <span>- R$ 0,00</span>
              </div>
              <div className="flex justify-between items-center text-xl font-black text-dark pt-2 border-t border-gray-200">
                <span>Total a Pagar na Loja:</span>
                <span className="text-primary">R$ {totalPrice.toFixed(2).replace('.', ',')}</span>
              </div>
            </div>
            
            {/* Botão de Finalizar no Resumo */}
            {isRegistrationComplete ? (
              <button onClick={handleFinish} className="w-full bg-primary hover:bg-orange-600 text-light font-bold py-4 rounded transition-colors text-lg shadow-md">
                Encomendar agora
              </button>
            ) : (
              <div className="text-center">
                <button 
                  onClick={() => navigate('/completar-cadastro?redirect=/checkout')} 
                  className="w-full bg-dark hover:bg-gray-800 text-light font-bold py-4 rounded transition-colors text-lg shadow-md animate-pulse"
                >
                  Complete seu cadastro para encomendar
                </button>
                <p className="text-xs text-gray-500 mt-3">
                  * O pagamento é feito presencialmente na retirada.
                </p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Seção Quem viu isto, também viu */}
      {recommendations.length > 0 && (
        <div className="mt-16 pt-8 border-t border-gray-200">
          <h2 className="text-2xl font-black text-dark mb-6 flex items-center gap-2">
            <span className="text-xl">👀</span> Quem viu isto, também gostou
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {recommendations.map(product => (
              <ProductCard key={`chk-${product.id}`} product={product} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
