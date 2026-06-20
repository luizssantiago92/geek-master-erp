import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import { supabase } from '../lib/supabase';
import { Filter } from 'lucide-react';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('Todos');

  const PRODUCT_TYPES = [
    'Todos',
    'Funko POP',
    'Caneca e Copo',
    'Action Figures',
    'Vestuário',
    'Acessórios'
  ];

  useEffect(() => {
    async function fetchProducts() {
      try {
        const { data, error } = await supabase
          .from('produtos')
          .select('*')
          .order('criado_em', { ascending: false });
          
        if (error) throw error;
        
        if (data) {
          const formattedProducts = data.map(item => ({
            id: item.id,
            title: item.nome.replace('[TESTE]', '').trim(),
            franchise: item.franquia || 'Geral',
            price: item.preco_base || 0,
            oldPrice: null, // Simulando que não há preço antigo
            discount: 0,
            isNew: item.nome.includes('[TESTE]'), 
            image: item.imagem_url || "https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&q=80&w=400"
          }));
          
          // Simulando desconto e oldPrice para exibir o UI de cupom baseado no Geral Geek
          // Vamos colocar 15% OFF em produtos acima de R$ 150 aleatoriamente (no mock)
          formattedProducts.forEach(p => {
            if (p.price > 150) {
              p.oldPrice = p.price;
              p.discount = 15;
              p.price = p.price * 0.85;
            }
          });

          setProducts(formattedProducts);
        }
      } catch (error) {
        console.error("Erro ao buscar produtos:", error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchProducts();
  }, []);

  const filteredProducts = products.filter(p => {
    if (selectedType === 'Todos') return true;
    const titleLower = p.title.toLowerCase();
    
    switch (selectedType) {
      case 'Funko POP':
        return titleLower.includes('funko');
      case 'Caneca e Copo':
        return titleLower.includes('caneca') || titleLower.includes('copo');
      case 'Action Figures':
        return titleLower.includes('action') || titleLower.includes('figure');
      case 'Vestuário':
        return titleLower.includes('camise') || titleLower.includes('roupa') || titleLower.includes('casaco');
      case 'Acessórios':
        return titleLower.includes('chaveiro') || titleLower.includes('colar') || titleLower.includes('anel') || titleLower.includes('pin');
      default:
        return true;
    }
  });

  return (
    <div className="w-full bg-gray-50 min-h-screen">
      <div className="container mx-auto px-4 py-8">
        
        {/* Top Header / Breadcrumb area similar to Geral Geek */}
        <div className="mb-6">
          <h1 className="text-3xl font-black text-dark mb-2">
            {selectedType === 'Todos' ? 'Catálogo Completo' : selectedType}
          </h1>
          <p className="text-sm text-gray-500">
            Home / Produtos / <span className="text-primary font-semibold">{selectedType}</span>
          </p>
        </div>

        {/* Banners Temáticos */}
        <div className="mb-10 mt-4 rounded-2xl overflow-hidden shadow-lg relative h-64 md:h-80 w-full group cursor-pointer bg-dark flex items-center justify-center">
          {/* Fundo do Banner */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-900 via-indigo-900 to-purple-900 opacity-90 transition-transform duration-700 group-hover:scale-105"></div>
          
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between w-full px-8 md:px-16">
            <div className="text-white text-center md:text-left">
              <span className="bg-yellow-400 text-dark font-black px-3 py-1 rounded-full text-xs tracking-wider uppercase mb-4 inline-block">Lançamento</span>
              <h2 className="text-4xl md:text-5xl font-black mb-3">Toy Story 5</h2>
              <p className="text-lg md:text-xl text-blue-200 font-medium mb-6 max-w-md">Ao infinito e além... A nova coleção exclusiva de Funkos já aterrissou na Master Geek!</p>
              <button className="bg-white text-dark font-bold px-8 py-3 rounded-full hover:bg-yellow-400 hover:text-dark transition-colors shadow-lg">Ver Coleção</button>
            </div>
            {/* Foto de destaque no banner (Jessie Funko) */}
            <div className="hidden md:block">
              <img src="https://funko.com.br/arquivos/ids/187989-1000-1000/Boneco-Funko-Pop--Disney-Toy-Story-5---Jessie-12856.jpg" alt="Jessie Funko" className="h-64 object-contain drop-shadow-2xl hover:scale-110 transition-transform duration-500 transform rotate-3" />
            </div>
          </div>
        </div>
        
        {/* Recomendados (Exibido acima do catálogo principal) */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-black text-dark flex items-center gap-2">
                <span className="text-2xl">✨</span> Recomendados para Você
              </h3>
              <p className="text-gray-500 text-sm mt-1">Baseado nas suas franquias favoritas (Marvel, DC, Disney)</p>
            </div>
            <button className="text-primary font-bold hover:underline text-sm hidden md:block">Ver mais recomendações</button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {/* Pegamos apenas 5 produtos para destaque que combinam com as preferências */}
            {products.slice(0, 5).map(product => (
              <ProductCard key={`rec-${product.id}`} product={product} />
            ))}
          </div>
        </div>

        {/* Separador */}
        <div className="w-full h-px bg-gray-200 my-10"></div>

        <div className="flex flex-col md:flex-row gap-8">
          
          {/* Sidebar / Filtros */}
          <aside className="w-full md:w-64 flex-shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 sticky top-24">
              <div className="flex items-center gap-2 font-bold text-dark mb-4 border-b border-gray-100 pb-3">
                <Filter size={18} />
                <span>Tipos de Produto</span>
              </div>
              
              <ul className="space-y-1">
                {PRODUCT_TYPES.map(type => (
                  <li key={type}>
                    <button
                      onClick={() => setSelectedType(type)}
                      className={`w-full text-left px-3 py-2 rounded transition-colors text-sm font-semibold
                        ${selectedType === type 
                          ? 'bg-dark text-white' 
                          : 'text-gray-600 hover:bg-gray-100 hover:text-dark'
                        }`}
                    >
                      {type}
                    </button>
                  </li>
                ))}
              </ul>

              <div className="mt-8 border-t border-gray-100 pt-4">
                <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 text-center">
                  <span className="text-xl">🚀</span>
                  <p className="text-sm font-bold text-primary mt-2">Destaque da Semana</p>
                  <p className="text-xs text-gray-600 mt-1">Coleção House of The Dragon</p>
                </div>
              </div>
            </div>
          </aside>

          {/* Grid Principal */}
          <main className="flex-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6 flex justify-between items-center">
              <span className="text-sm font-semibold text-gray-600">
                Encontrados <span className="text-dark font-bold">{filteredProducts.length}</span> produtos
              </span>
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-500">Ordenar por:</label>
                <select className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-primary">
                  <option>Relevância</option>
                  <option>Menor Preço</option>
                  <option>Maior Preço</option>
                  <option>Lançamentos</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
              {loading ? (
                <div className="col-span-full text-center py-12 text-gray-500">
                  <div className="animate-pulse flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                    <p>Carregando catálogo...</p>
                  </div>
                </div>
              ) : filteredProducts.length > 0 ? (
                filteredProducts.map(product => (
                  <ProductCard key={product.id} product={product} />
                ))
              ) : (
                <div className="col-span-full text-center py-16 bg-white rounded-xl border border-gray-100">
                  <p className="text-gray-500 mb-4">Nenhum produto encontrado nesta categoria.</p>
                  <button 
                    onClick={() => setSelectedType('Todos')}
                    className="text-primary font-bold hover:underline"
                  >
                    Ver todos os produtos
                  </button>
                </div>
              )}
            </div>
          </main>

        </div>
      </div>
    </div>
  );
}
