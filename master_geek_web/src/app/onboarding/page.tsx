'use client'

import { useState } from 'react'
import { Check, ChevronRight } from 'lucide-react'
import Link from 'next/link'

// Exemplo de avatares com base no mascote gerado e na temática
const AVATARS = [
  { id: '1', name: 'Piticão Clássico', url: '/avatar_padrao.png' }, // Aqui entrará a imagem real que geramos
  { id: '2', name: 'Piticão Rocker', url: '/avatar_rock.png' }, 
  { id: '3', name: 'Piticão Anime', url: '/avatar_anime.png' },
]

// Baseado na raspagem mental de Piticas, Zona Criativa e Funko
const FRANCHISES = [
  { id: 'marvel', name: 'Marvel', color: 'bg-red-600' },
  { id: 'dc', name: 'DC Comics', color: 'bg-blue-800' },
  { id: 'star_wars', name: 'Star Wars', color: 'bg-zinc-900' },
  { id: 'harry_potter', name: 'Harry Potter', color: 'bg-amber-700' },
  { id: 'animes', name: 'Animes (Naruto, DBZ...)', color: 'bg-orange-500' },
  { id: 'disney', name: 'Disney & Pixar', color: 'bg-blue-400' },
  { id: 'series', name: 'Séries (Stranger Things, etc)', color: 'bg-purple-700' },
  { id: 'games', name: 'Games (Mario, Sonic...)', color: 'bg-green-600' },
]

export default function Onboarding() {
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null)
  const [selectedFranchises, setSelectedFranchises] = useState<string[]>([])

  const toggleFranchise = (id: string) => {
    if (selectedFranchises.includes(id)) {
      setSelectedFranchises(selectedFranchises.filter(f => f !== id))
    } else {
      setSelectedFranchises([...selectedFranchises, id])
    }
  }

  const isReady = selectedAvatar !== null && selectedFranchises.length >= 3

  return (
    <main className="min-h-screen bg-piticas-dark text-white font-sans p-8 md:p-16">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-black tracking-tighter mb-4">
          Quem está assist... digo, <span className="text-piticas-orange">COMPRANDO?</span>
        </h1>
        <p className="text-gray-400 text-lg mb-12">
          Personalize sua experiência na Piticas Rio. Escolha seu avatar e pelo menos 3 franquias que você ama.
        </p>

        {/* Step 1: Avatar */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-piticas-orange text-white flex items-center justify-center text-sm">1</span>
            Escolha seu Avatar
          </h2>
          <div className="flex gap-6 overflow-x-auto pb-4">
            {AVATARS.map((avatar) => (
              <div 
                key={avatar.id}
                onClick={() => setSelectedAvatar(avatar.id)}
                className={`relative flex-shrink-0 w-32 h-32 rounded-xl cursor-pointer transition-all duration-300 border-4 
                  ${selectedAvatar === avatar.id ? 'border-piticas-orange scale-105 shadow-[0_0_20px_rgba(255,90,0,0.5)]' : 'border-transparent hover:border-gray-500'}`}
              >
                {/* Aqui vai a tag <img src={avatar.url} /> depois de colocarmos na pasta public */}
                <div className="w-full h-full bg-piticas-gray rounded-lg flex items-center justify-center text-center text-xs p-2 text-gray-500">
                  Foto: {avatar.name}
                </div>
                {selectedAvatar === avatar.id && (
                  <div className="absolute -top-3 -right-3 bg-piticas-orange p-1 rounded-full text-white">
                    <Check className="w-5 h-5" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Step 2: Franquias */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <span className="w-8 h-8 rounded-full bg-piticas-orange text-white flex items-center justify-center text-sm">2</span>
            Suas Franquias Favoritas
          </h2>
          <p className="text-sm text-gray-500 mb-6 -mt-4 ml-10">
            Selecione no mínimo 3 ({selectedFranchises.length}/3)
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {FRANCHISES.map((franchise) => {
              const isSelected = selectedFranchises.includes(franchise.id)
              return (
                <div
                  key={franchise.id}
                  onClick={() => toggleFranchise(franchise.id)}
                  className={`
                    relative h-24 rounded-xl cursor-pointer overflow-hidden transition-all duration-300
                    ${isSelected ? 'ring-4 ring-piticas-orange scale-105' : 'hover:scale-105 opacity-80 hover:opacity-100'}
                    ${franchise.color}
                  `}
                >
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center p-4 text-center">
                    <span className="font-bold text-sm md:text-base drop-shadow-md">{franchise.name}</span>
                  </div>
                  {isSelected && (
                    <div className="absolute top-2 right-2 bg-piticas-orange p-1 rounded-full text-white">
                      <Check className="w-3 h-3" />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>

        {/* Action Button */}
        <div className="flex justify-end border-t border-white/10 pt-8">
          <button 
            disabled={!isReady}
            className={`
              flex items-center gap-2 px-8 py-4 rounded font-bold text-lg transition-all
              ${isReady 
                ? 'bg-piticas-orange hover:bg-orange-600 text-white shadow-[0_0_15px_rgba(255,90,0,0.5)] hover:shadow-[0_0_25px_rgba(255,90,0,0.8)] cursor-pointer' 
                : 'bg-gray-800 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            Começar Minha Saga
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </main>
  )
}
