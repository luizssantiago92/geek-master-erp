import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Onboarding() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedFranchises, setSelectedFranchises] = useState([]);

  // URL parameters to get redirect if exists
  const searchParams = new URLSearchParams(location.search);
  const redirectUrl = searchParams.get('redirect') || '/';

  const franchises = [
    { id: 'marvel', name: 'Marvel', img: 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?auto=format&fit=crop&q=80&w=400' },
    { id: 'starwars', name: 'Star Wars', img: 'https://images.unsplash.com/photo-1608889175123-8ee362201f81?auto=format&fit=crop&q=80&w=400' },
    { id: 'harrypotter', name: 'Harry Potter', img: 'https://images.unsplash.com/photo-1547756536-cde3673fa2e5?auto=format&fit=crop&q=80&w=400' },
    { id: 'dc', name: 'DC Comics', img: 'https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?auto=format&fit=crop&q=80&w=400' },
    { id: 'anime', name: 'Animes', img: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&q=80&w=400' },
    { id: 'games', name: 'Games', img: 'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?auto=format&fit=crop&q=80&w=400' },
    { id: 'lotr', name: 'Senhor dos Anéis', img: 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?auto=format&fit=crop&q=80&w=400' },
    { id: 'disney', name: 'Disney', img: 'https://images.unsplash.com/photo-1518063319789-7217e6706b04?auto=format&fit=crop&q=80&w=400' },
  ];

  const toggleFranchise = (id) => {
    setSelectedFranchises(prev => {
      if (prev.includes(id)) {
        return prev.filter(f => f !== id);
      } else {
        if (prev.length >= 3) {
          alert('Você pode selecionar no máximo 3 franquias!');
          return prev;
        }
        return [...prev, id];
      }
    });
  };

  const handleFinish = () => {
    // Save preferences to supabase profiles table
    console.log("Preferências salvas:", selectedFranchises);
    navigate(redirectUrl);
  };

  const handleSkip = () => {
    navigate(redirectUrl);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-dark py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full text-center">
        
        <h1 className="text-4xl md:text-5xl font-black text-light mb-4">
          Quem é você no multiverso?
        </h1>
        <p className="text-gray-300 text-lg mb-12">
          Selecione **até 3** de suas franquias favoritas para personalizarmos seu catálogo e avisarmos sobre novidades imperdíveis.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-12">
          {franchises.map(franchise => {
            const isSelected = selectedFranchises.includes(franchise.id);
            return (
              <button
                key={franchise.id}
                onClick={() => toggleFranchise(franchise.id)}
                className={`
                  relative flex flex-col items-center justify-center rounded-xl overflow-hidden border-4 transition-all h-40
                  ${isSelected 
                    ? 'border-primary shadow-[0_0_15px_rgba(255,87,34,0.6)] scale-105' 
                    : 'border-transparent hover:border-gray-500'
                  }
                `}
              >
                <div className="absolute inset-0 bg-black/40 z-10 pointer-events-none group-hover:bg-black/20 transition-colors"></div>
                <img src={franchise.img} alt={franchise.name} className="absolute inset-0 w-full h-full object-cover" />
                <span className="relative z-20 font-bold text-lg text-white drop-shadow-md bg-black/50 w-full py-1">
                  {franchise.name}
                </span>
                
                {isSelected && (
                  <div className="absolute top-2 right-2 z-20 bg-primary text-white rounded-full w-6 h-6 flex items-center justify-center font-bold">
                    ✓
                  </div>
                )}
              </button>
            );
          })}
        </div>

        <button
          onClick={handleFinish}
          disabled={selectedFranchises.length === 0}
          className="bg-primary hover:bg-orange-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-light font-bold text-lg px-12 py-4 rounded-full transition-colors shadow-lg"
        >
          {selectedFranchises.length === 0 ? 'Selecione de 1 a 3 franquias' : 'Continuar e Concluir'}
        </button>
        
        <div className="mt-6">
          <button onClick={handleSkip} className="text-gray-400 hover:text-light text-sm underline">
            Pular esta etapa por enquanto
          </button>
        </div>

      </div>
    </div>
  );
}
