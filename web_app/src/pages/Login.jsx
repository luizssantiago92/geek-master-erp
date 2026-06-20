import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { Mail } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useUser();
  const [showEmailForm, setShowEmailForm] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    login({
      name: 'Novo Usuário',
      email: email,
      photoUrl: '',
      provider: 'email',
      hasPassword: true
    });
    navigate({ pathname: '/completar-cadastro', search: window.location.search });
  };

  const handleSocialAuth = (provider) => {
    // Simulando que o Google/Facebook puxa os dados do usuário
    const mockUser = {
      name: 'João da Silva',
      email: `joao.${provider}@exemplo.com`,
      photoUrl: 'https://i.imgur.com/GzB9t1n.jpeg', // Foto temporária para mock
      provider: provider,
      hasPassword: false
    };
    login(mockUser);
    navigate({ pathname: '/completar-cadastro', search: window.location.search });
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        
        {/* Banner/Header */}
        <div className="bg-dark text-center py-6">
          <div className="bg-primary text-light font-bold text-3xl p-2 rounded-lg inline-block mb-2">
            Piticas Rio
          </div>
          <h2 className="text-light text-xl font-bold">
            Acesse ou crie sua conta
          </h2>
        </div>

        <div className="p-8 space-y-4">
          
          {/* Social Buttons */}
          <button 
            onClick={() => handleSocialAuth('Google')}
            className="w-full bg-white border border-gray-300 text-dark font-semibold py-3 rounded flex items-center justify-center gap-3 hover:bg-gray-50 transition-colors shadow-sm"
          >
            <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-6 h-6" />
            Continuar com Google
          </button>
          
          <button 
            onClick={() => handleSocialAuth('Facebook')}
            className="w-full bg-[#1877F2] text-white font-semibold py-3 rounded flex items-center justify-center gap-3 hover:bg-[#166FE5] transition-colors shadow-sm"
          >
            <img src="https://www.svgrepo.com/show/475647/facebook-color.svg" alt="Facebook" className="w-6 h-6 bg-white rounded-full p-0.5" />
            Continuar com Facebook
          </button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Ou use seu e-mail</span>
            </div>
          </div>

          {!showEmailForm ? (
            <button 
              onClick={() => setShowEmailForm(true)}
              className="w-full bg-dark text-light font-semibold py-3 rounded flex items-center justify-center gap-2 hover:bg-gray-800 transition-colors"
            >
              <Mail size={20} />
              Logar com E-mail
            </button>
          ) : (
            <form onSubmit={handleEmailAuth} className="space-y-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Email</label>
                <input 
                  type="email" 
                  required
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none bg-white"
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
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none bg-white"
                  placeholder="••••••••"
                />
              </div>
              <button 
                type="submit" 
                className="w-full bg-primary text-light font-bold py-3 rounded hover:bg-orange-600 transition-colors shadow-sm"
              >
                Entrar / Registrar
              </button>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}
