import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { useNavigate } from 'react-router-dom';

export default function Checkout() {
  const { cart, totalPrice, clearCart } = useCart();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    cpf: '',
    phone: '',
    kiosk: 'norteshopping'
  });

  if (cart.length === 0) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-4">Sua encomenda está vazia</h2>
        <button onClick={() => navigate('/')} className="text-primary hover:underline">Voltar ao catálogo</button>
      </div>
    );
  }

  const handleFinish = (e) => {
    e.preventDefault();
    // Save to supabase `encomendas` table here
    alert('Encomenda realizada com sucesso! Você receberá as atualizações no WhatsApp.');
    clearCart();
    navigate('/');
  };

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
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                value={formData.kiosk}
                onChange={e => setFormData({...formData, kiosk: e.target.value})}
              >
                <option value="norteshopping">Norte Shopping - RJ</option>
                <option value="barrashopping">Barra Shopping - RJ</option>
                <option value="novaamerica">Nova América - RJ</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">CPF (Obrigatório para retirada)</label>
              <input 
                type="text" 
                required
                placeholder="000.000.000-00"
                value={formData.cpf}
                onChange={e => setFormData({...formData, cpf: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">WhatsApp (Para avisarmos quando chegar)</label>
              <input 
                type="text" 
                required
                placeholder="(00) 00000-0000"
                value={formData.phone}
                onChange={e => setFormData({...formData, phone: e.target.value})}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
              />
            </div>

            <div className="pt-4 border-t border-gray-100 mt-6">
              <button type="submit" className="w-full bg-primary hover:bg-orange-600 text-light font-bold py-3 rounded transition-colors text-lg">
                Confirmar Reserva
              </button>
              <p className="text-xs text-center text-gray-500 mt-3">
                * O pagamento é feito presencialmente no ato da retirada.
              </p>
            </div>

          </form>
        </div>

        {/* Order Summary */}
        <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
          <h2 className="text-xl font-bold mb-6">Resumo da Encomenda</h2>
          <div className="space-y-4 mb-6">
            {cart.map(item => (
              <div key={item.id} className="flex justify-between text-sm">
                <span className="text-gray-600 line-clamp-1 pr-4">{item.quantity}x {item.title}</span>
                <span className="font-semibold text-dark whitespace-nowrap">R$ {(item.price * item.quantity).toFixed(2).replace('.', ',')}</span>
              </div>
            ))}
          </div>
          <div className="border-t border-gray-200 pt-4 flex justify-between items-center text-lg font-black text-dark">
            <span>Total a Pagar na Loja:</span>
            <span className="text-primary">R$ {totalPrice.toFixed(2).replace('.', ',')}</span>
          </div>
        </div>

      </div>
    </div>
  );
}
