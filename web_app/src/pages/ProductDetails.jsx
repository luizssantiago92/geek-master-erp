import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { useCart } from '../contexts/CartContext';
import ProductCard from '../components/ProductCard';
import { ShoppingCart, ArrowLeft, ShieldCheck, Truck } from 'lucide-react';

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [mainImage, setMainImage] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    async function fetchProduct() {
      setLoading(true);
      const { data } = await supabase.from('produtos').select('*').eq('id', id).single();
      
      if (data) {
        // Fallback robusto caso as colunas novas ainda não tenham sido preenchidas
        const prod = {
          id: data.id,
          title: data.nome.replace('[TESTE]', '').trim(),
          franchise: data.franquia || 'Geral',
          price: data.preco_base || 0,
          isNew: data.is_new || data.nome.includes('[TESTE]'),
          description: data.descricao || "Produto oficial e original com detalhes impressionantes. Perfeito para completar sua coleção ou presentear alguém especial.",
          image: data.imagem_url || "https://funko.com.br/arquivos/ids/160000-1000-1000/generico.jpg",
          gallery: data.imagens_galeria || [data.imagem_url]
        };
        setProduct(prod);
        setMainImage(prod.image);
        
        // Puxar recomendações
        const { data: recsData } = await supabase.from('produtos').select('*').neq('id', id).limit(4);
        if (recsData) {
          setRecommendations(recsData.map(item => ({
            id: item.id,
            title: item.nome.replace('[TESTE]', '').trim(),
            franchise: item.franquia || 'Geral',
            price: item.preco_base || 0,
            isNew: item.nome.includes('[TESTE]'), 
            image: item.imagem_url
          })));
        }
      }
      setLoading(false);
    }
    fetchProduct();
  }, [id]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Carregando detalhes do produto...</div>;
  }

  if (!product) {
    return <div className="min-h-screen flex flex-col items-center justify-center"><h2 className="text-2xl font-bold">Produto não encontrado</h2><button onClick={() => navigate('/')} className="mt-4 text-primary hover:underline">Voltar para a Home</button></div>;
  }

  const handleAddToCart = () => {
    // Adiciona ao carrinho respeitando a quantidade selecionada
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
    alert(`${quantity}x ${product.title} adicionado à sua encomenda! Você pode continuar navegando ou ir para o checkout clicando no carrinho.`);
    navigate('/'); // Opcional: volta pra home para "Continuar no catalogo"
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Botão Voltar */}
      <button onClick={() => navigate(-1)} className="flex items-center text-gray-500 hover:text-dark mb-6 transition-colors">
        <ArrowLeft size={20} className="mr-2" />
        Voltar para o catálogo
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-16">
        <div className="flex flex-col md:flex-row">
          
          {/* Lado Esquerdo: Galeria de Imagens */}
          <div className="md:w-1/2 p-6 flex flex-col-reverse md:flex-row gap-4">
            {/* Miniaturas */}
            <div className="flex md:flex-col gap-3 overflow-x-auto md:overflow-visible w-full md:w-20">
              {product.gallery.map((img, index) => (
                <button 
                  key={index} 
                  onMouseEnter={() => setMainImage(img)}
                  onClick={() => setMainImage(img)}
                  className={`w-16 h-16 rounded-lg border-2 overflow-hidden flex-shrink-0 transition-all ${mainImage === img ? 'border-primary' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <img src={img} alt={`Thumb ${index}`} className="w-full h-full object-contain" />
                </button>
              ))}
            </div>
            {/* Imagem Principal */}
            <div className="flex-1 bg-gray-50 rounded-xl flex items-center justify-center p-8 border border-gray-100">
              <img src={mainImage} alt={product.title} className="w-full h-auto max-h-[500px] object-contain drop-shadow-xl transition-transform hover:scale-105 duration-300" />
            </div>
          </div>

          {/* Lado Direito: Informações e Compra */}
          <div className="md:w-1/2 p-8 md:p-12 flex flex-col justify-center">
            {product.isNew && (
              <span className="bg-primary text-white text-xs font-black uppercase tracking-widest px-3 py-1 rounded-full w-fit mb-4">Lançamento</span>
            )}
            
            <p className="text-gray-500 font-medium uppercase tracking-wider text-sm mb-2">{product.franchise}</p>
            <h1 className="text-3xl md:text-4xl font-black text-dark mb-4 leading-tight">{product.title}</h1>
            
            <div className="text-4xl font-black text-dark mb-6">
              R$ {product.price.toFixed(2).replace('.', ',')}
              <span className="block text-sm text-gray-500 font-medium mt-1">
                Em até {Math.max(1, Math.min(5, Math.floor(product.price / 60)))}x sem juros no cartão de crédito
              </span>
            </div>

            <p className="text-gray-600 mb-8 leading-relaxed">
              {product.description}
            </p>

            {/* Ações de Compra */}
            <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 mb-6">
              <div className="flex items-center gap-4 mb-4">
                <label className="font-bold text-dark">Quantidade:</label>
                <div className="flex items-center bg-white border border-gray-300 rounded-lg overflow-hidden">
                  <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="px-4 py-2 hover:bg-gray-100 text-dark font-bold">-</button>
                  <span className="px-4 py-2 font-bold w-12 text-center border-x border-gray-300">{quantity}</span>
                  <button onClick={() => setQuantity(Math.max(1, Math.min(3, quantity + 1)))} className="px-4 py-2 hover:bg-gray-100 text-dark font-bold">+</button>
                </div>
              </div>

              <button 
                onClick={handleAddToCart}
                className="w-full bg-dark hover:bg-gray-800 text-white font-black py-4 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-lg hover:scale-[1.02]"
              >
                <ShoppingCart size={24} />
                ENCOMENDAR E CONTINUAR NO CATÁLOGO
              </button>
            </div>

            {/* Badges de Confiança */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <ShieldCheck className="text-green-500" size={24} />
                <span>Produto 100% Original e Licenciado</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <Truck className="text-blue-500" size={24} />
                <span>Retire seu pedido no quiosque mais proximo da sua casa</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Seção Recomendados Relacionados */}
      {recommendations.length > 0 && (
        <div className="mt-16 mb-8">
          <h2 className="text-2xl font-black text-dark mb-8 text-center uppercase tracking-widest">Quem viu isto, também viu</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {recommendations.map(product => (
              <ProductCard key={`rec-prod-${product.id}`} product={product} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
