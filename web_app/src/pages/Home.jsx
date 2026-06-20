import React from 'react';
import ProductCard from '../components/ProductCard';

export default function Home() {
  // Mock data for initial layout testing
  const mockProducts = [
    {
      id: 1,
      title: "Funko Pop Dunk - A Knight Of The Seven Kingdoms #1901",
      franchise: "Game of Thrones",
      price: 144.99,
      oldPrice: 162.91,
      discount: 11,
      isNew: true,
      image: "https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&q=80&w=400"
    },
    {
      id: 2,
      title: "Camiseta Star Wars Darth Vader Dark Side - Preta",
      franchise: "Star Wars",
      price: 89.90,
      oldPrice: null,
      discount: 0,
      isNew: false,
      image: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&q=80&w=400"
    },
    {
      id: 3,
      title: "Caneca Mágica Harry Potter Mapa do Maroto",
      franchise: "Harry Potter",
      price: 59.90,
      oldPrice: 79.90,
      discount: 25,
      isNew: false,
      image: "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&q=80&w=400"
    },
    {
      id: 4,
      title: "Action Figure Homem-Aranha Miles Morales 15cm",
      franchise: "Marvel",
      price: 299.90,
      oldPrice: 349.90,
      discount: 14,
      isNew: true,
      image: "https://images.unsplash.com/photo-1608889476561-6242cb816d1e?auto=format&fit=crop&q=80&w=400"
    }
  ];

  return (
    <div className="w-full">
      {/* Hero Banner Area */}
      <div className="bg-dark w-full h-[400px] relative flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 opacity-40 bg-[url('https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&q=80&w=1200')] bg-cover bg-center"></div>
        <div className="relative z-10 text-center px-4">
          <span className="bg-accent text-dark font-black px-4 py-1 rounded-full text-sm mb-4 inline-block tracking-wider uppercase">
            Especial Lançamento
          </span>
          <h1 className="text-4xl md:text-6xl font-black text-light mb-4 text-shadow-lg">
            Sua coleção <span className="text-primary">começa aqui.</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-2xl mx-auto">
            Reserve agora seus produtos favoritos e retire no quiosque Piticão mais próximo. Sem frete, sem dor de cabeça.
          </p>
          <button className="bg-primary hover:bg-orange-600 text-light font-bold text-lg px-8 py-3 rounded-full transition-transform hover:scale-105 shadow-lg">
            Ver Novidades
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="container mx-auto px-4 py-12">
        
        {/* Section: Novidades */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-4">
            <h2 className="text-2xl font-bold text-dark flex items-center gap-2">
              <span className="text-primary">🔥</span> Lançamentos da Semana
            </h2>
            <button className="text-sm font-semibold text-primary hover:text-orange-700">
              Ver Todos
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {mockProducts.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>

        {/* Section: Categorias */}
        <div className="mb-12 bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          <h2 className="text-2xl font-bold text-dark text-center mb-8">
            Navegue por Franquias
          </h2>
          <div className="flex flex-wrap justify-center gap-4">
            {["Marvel", "Star Wars", "Harry Potter", "DC Comics", "Animes", "Séries"].map(tag => (
              <button key={tag} className="bg-gray-50 hover:bg-accent hover:text-dark text-gray-700 font-semibold px-6 py-3 rounded-full border border-gray-200 transition-colors shadow-sm">
                {tag}
              </button>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
