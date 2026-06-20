import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';

export default function Login() {
  const navigate = useNavigate();
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    if (isRegistering) {
      // In production, we would use supabase.auth.signUp
      alert("Cadastro iniciado! Indo para a tela de preferências...");
      navigate('/onboarding');
    } else {
      // supabase.auth.signInWithPassword
      alert("Login efetuado!");
      navigate('/');
    }
  };

  const handleSocialAuth = (provider) => {
    // supabase.auth.signInWithOAuth({ provider })
    alert(`Redirecionando para o ${provider}...`);
    navigate('/onboarding');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        
        {/* Banner/Header */}
        <div className="bg-dark text-center py-6">
          <div className="bg-primary text-light font-bold text-3xl p-2 rounded-lg inline-block mb-2">
            Piticão
          </div>
          <h2 className="text-light text-xl font-bold">
            {isRegistering ? 'Crie sua conta' : 'Acesse sua conta'}
          </h2>
        </div>

        <div className="p-8">
          <form onSubmit={handleEmailAuth} className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
              <input 
                type="email" 
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                placeholder="seu@email.com"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Senha</label>
              <input 
                type="password" 
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                placeholder="••••••••"
              />
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-dark text-light font-bold py-3 rounded hover:bg-primary transition-colors"
            >
              {isRegistering ? 'Registrar' : 'Entrar'}
            </button>
          </form>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Ou entre com</span>
            </div>
          </div>

          <div className="space-y-3">
            <button 
              onClick={() => handleSocialAuth('google')}
              className="w-full bg-red-600 text-white font-semibold py-3 rounded flex items-center justify-center gap-2 hover:bg-red-700 transition-colors"
            >
              Google
            </button>
            <button 
              onClick={() => handleSocialAuth('facebook')}
              className="w-full bg-blue-600 text-white font-semibold py-3 rounded flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors"
            >
              Facebook
            </button>
          </div>

          <div className="mt-8 text-center text-sm text-gray-600">
            {isRegistering ? (
              <p>Já possui cadastro? <button type="button" onClick={() => setIsRegistering(false)} className="font-bold text-primary hover:underline">Entre agora!</button></p>
            ) : (
              <p>Não possui cadastro? <button type="button" onClick={() => setIsRegistering(true)} className="font-bold text-primary hover:underline">Registre-se agora!</button></p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
