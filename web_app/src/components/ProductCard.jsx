import React from 'react';
import { Heart, ShoppingBag } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  // Lógica de Parcelamento
  const parcelasPossiveis = Math.floor(product.price / 60);
  const maxInstallments = Math.min(5, parcelasPossiveis);
  const isBilledInInstallments = maxInstallments >= 2;
  const installmentValue = isBilledInInstallments ? (product.price / maxInstallments).toFixed(2).replace('.', ',') : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition-all group relative flex flex-col">
      {/* Badges */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
        {product.isNew && (
          <span className="bg-primary text-light text-[10px] font-bold px-2 py-1 rounded shadow-sm">
            NOVIDADE
          </span>
        )}
        {product.discount > 0 && (
          <span className="bg-green-600 text-light text-[10px] font-bold px-2 py-1 rounded shadow-sm">
            {product.discount}% OFF
          </span>
        )}
      </div>

      <div className="absolute top-2 right-2 z-10">
        <button className="bg-white/80 p-1.5 rounded-full hover:bg-red-50 hover:text-red-500 transition-colors shadow-sm">
          <Heart size={18} className="text-gray-400 hover:text-red-500" />
        </button>
      </div>

      {/* Image */}
      <Link to={`/produto/${product.id}`} className="block relative aspect-square overflow-hidden bg-gray-50">
        <img 
          src={product.image} 
          alt={product.title}
          className="object-contain w-full h-full p-4 group-hover:scale-105 transition-transform duration-300"
        />
      </Link>

      {/* Content */}
      <div className="p-4 flex flex-col flex-1">
        <div className="text-xs text-gray-500 mb-1 font-semibold">{product.franchise}</div>
        <Link to={`/produto/${product.id}`}>
          <h3 className="text-sm font-bold text-dark leading-tight mb-2 hover:text-primary transition-colors line-clamp-2">
            {product.title}
          </h3>
        </Link>

        <div className="mt-auto">
          {product.oldPrice && (
            <div className="text-xs text-gray-400 line-through">
              R$ {product.oldPrice.toFixed(2).replace('.', ',')}
            </div>
          )}
          <div className="flex items-end gap-2">
            <div className="text-lg font-black text-dark">
              R$ {product.price.toFixed(2).replace('.', ',')}
            </div>
          </div>
          <div className="text-[10px] text-green-700 font-semibold mb-3 h-4">
            {isBilledInInstallments ? (
              <span>até {maxInstallments}x de R$ {installmentValue} sem juros</span>
            ) : (
              <span>à vista</span>
            )}
          </div>

          <button 
            onClick={() => addToCart(product)}
            className="w-full bg-dark hover:bg-primary text-light py-2 rounded font-bold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            <ShoppingBag size={16} />
            Encomendar
          </button>
        </div>
      </div>
    </div>
  );
}
