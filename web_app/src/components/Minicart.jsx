import React from 'react';
import { useCart } from '../contexts/CartContext';
import { X, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Minicart() {
  const { cart, removeFromCart, totalPrice, isCartOpen, setIsCartOpen } = useCart();
  const navigate = useNavigate();

  if (!isCartOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 z-50" 
        onClick={() => setIsCartOpen(false)}
      ></div>
      <div className="fixed top-0 right-0 h-full w-full max-w-md bg-white z-50 shadow-2xl flex flex-col">
        
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <h2 className="text-xl font-bold text-dark">Sua Encomenda</h2>
          <button onClick={() => setIsCartOpen(false)} className="text-gray-500 hover:text-dark">
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {cart.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <p>Sua lista de encomenda está vazia.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cart.map(item => (
                <div key={item.id} className="flex gap-4 border border-gray-100 rounded-lg p-3 relative">
                  <img src={item.image} alt={item.title} className="w-20 h-20 object-contain bg-gray-50 rounded" />
                  <div className="flex-1">
                    <h3 className="text-sm font-bold text-dark line-clamp-2 mb-1">{item.title}</h3>
                    <div className="text-xs text-gray-500 mb-2">Qtd: {item.quantity}</div>
                    <div className="font-bold text-primary">R$ {(item.price * item.quantity).toFixed(2).replace('.', ',')}</div>
                  </div>
                  <button 
                    onClick={() => removeFromCart(item.id)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-500"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {cart.length > 0 && (
          <div className="p-4 border-t border-gray-100 bg-gray-50">
            <div className="flex justify-between items-center mb-4 text-lg font-bold text-dark">
              <span>Total Estimado:</span>
              <span>R$ {totalPrice.toFixed(2).replace('.', ',')}</span>
            </div>
            <button 
              onClick={() => {
                setIsCartOpen(false);
                navigate('/checkout');
              }}
              className="w-full bg-dark hover:bg-primary text-light font-bold py-3 rounded transition-colors"
            >
              Fechar Encomenda (Retirada)
            </button>
          </div>
        )}

      </div>
    </>
  );
}
