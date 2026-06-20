import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Onboarding() {
  const navigate = useNavigate();
  const [selectedFranchises, setSelectedFranchises] = useState([]);

  const franchises = [
    { id: 'marvel', name: 'Marvel', icon: '🦸‍♂️' },
    { id: 'starwars', name: 'Star Wars', icon: '⚔️' },
    { id: 'harrypotter', name: 'Harry Potter', icon: '⚡' },
    { id: 'dc', name: 'DC Comics', icon: '🦇' },
    { id: 'anime', name: 'Animes (Geral)', icon: '🍜' },
    { id: 'games', name: 'Games', icon: '🎮' },
    { id: 'lotr', name: 'Senhor dos Anéis', icon: '🧝' },
    { id: 'disney', name: 'Disney', icon: '✨' },
  ];

  const toggleFranchise = (id) => {
    setSelectedFranchises(prev => 
      prev.includes(id) 
        ? prev.filter(f => f !== id)
        : [...prev, id]
    );
  };

  const handleFinish = () => {
    // Save preferences to supabase profiles table
    console.log("Preferências salvas:", selectedFranchises);
    navigate('/');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-dark py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full text-center">
        
        <h1 className="text-4xl md:text-5xl font-black text-light mb-4">
          Quem é você no multiverso?
        </h1>
        <p className="text-gray-300 text-lg mb-12">
          Selecione suas franquias favoritas para personalizarmos seu catálogo e avisarmos sobre novidades imperdíveis.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-12">
          {franchises.map(franchise => {
            const isSelected = selectedFranchises.includes(franchise.id);
            return (
              <button
                key={franchise.id}
                onClick={() => toggleFranchise(franchise.id)}
                className={`
                  flex flex-col items-center justify-center p-6 rounded-xl border-2 transition-all
                  ${isSelected 
                    ? 'border-primary bg-primary/20 text-light scale-105' 
                    : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-500 hover:text-gray-200'
                  }
                `}
              >
                <span className="text-4xl mb-2">{franchise.icon}</span>
                <span className="font-bold text-sm">{franchise.name}</span>
              </button>
            );
          })}
        </div>

        <button
          onClick={handleFinish}
          disabled={selectedFranchises.length === 0}
          className="bg-primary hover:bg-orange-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-light font-bold text-lg px-12 py-4 rounded-full transition-colors shadow-lg"
        >
          {selectedFranchises.length === 0 ? 'Selecione pelo menos uma' : 'Continuar'}
        </button>
        
        <div className="mt-6">
          <button onClick={() => navigate('/')} className="text-gray-400 hover:text-light text-sm underline">
            Pular esta etapa por enquanto
          </button>
        </div>

      </div>
    </div>
  );
}
