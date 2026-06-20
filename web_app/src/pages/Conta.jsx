import React, { useState } from 'react';
import { useUser } from '../contexts/UserContext';
import { useNavigate } from 'react-router-dom';
import { Check } from 'lucide-react';

const AVATARES = [
  { id: 'wolverine', name: 'Wolverine', url: 'https://i.imgur.com/8Qe8Z3M.jpeg' },
  { id: 'vegeta', name: 'Vegeta', url: 'https://i.imgur.com/GzB9t1n.jpeg' },
  { id: 'darth_vader', name: 'Darth Vader', url: 'https://i.imgur.com/uT27pT6.jpeg' },
  { id: 'mandalorian', name: 'Mandalorian', url: 'https://i.imgur.com/19O2s0f.jpeg' },
  { id: 'goku', name: 'Goku', url: 'https://i.imgur.com/N71u3Fq.jpeg' }
];

export default function Conta() {
  const { user, updateUser } = useUser();
  const navigate = useNavigate();
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  if (!user) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold mb-4">Você não está logado.</h2>
        <button onClick={() => navigate('/login')} className="text-primary hover:underline">Ir para Login</button>
      </div>
    );
  }

  const handleSelectAvatar = (url) => {
    updateUser({ photoUrl: url });
    setSuccessMsg('Avatar atualizado com sucesso!');
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  const handleSavePassword = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("As senhas não coincidem!");
      return;
    }
    if (password.length < 6) {
      alert("A senha deve ter no mínimo 6 caracteres.");
      return;
    }
    // No protótipo, apenas atualizamos a flag localmente
    updateUser({ hasPassword: true });
    setSuccessMsg('Senha adicionada com sucesso!');
    setPassword('');
    setConfirmPassword('');
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-2xl">
      <h1 className="text-3xl font-black text-dark mb-8">Minha Conta</h1>
      
      {successMsg && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-6" role="alert">
          <span className="block sm:inline">{successMsg}</span>
        </div>
      )}

      {/* Dados do Perfil */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-xl font-bold mb-4">Dados Principais</h2>
        <div className="flex items-center gap-6">
          <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-primary bg-gray-200">
            {user.photoUrl ? (
              <img src={user.photoUrl} alt="Perfil" className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-500 font-bold text-3xl">
                {user.name.charAt(0)}
              </div>
            )}
          </div>
          <div>
            <p className="font-bold text-lg">{user.name}</p>
            <p className="text-gray-600">{user.email}</p>
            {user.provider && (
              <p className="text-sm text-primary font-semibold mt-1">Conectado via {user.provider}</p>
            )}
          </div>
        </div>
      </div>

      {/* Alterar Avatar */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-xl font-bold mb-4">Mudar Avatar</h2>
        <p className="text-sm text-gray-600 mb-4">Escolha um personagem para o seu perfil.</p>
        <div className="flex flex-wrap gap-4">
          {AVATARES.map(avatar => (
            <button 
              key={avatar.id}
              onClick={() => handleSelectAvatar(avatar.url)}
              className={`relative w-20 h-20 rounded-full overflow-hidden border-4 transition-all hover:scale-105 ${user.photoUrl === avatar.url ? 'border-primary shadow-lg' : 'border-transparent'}`}
            >
              <img src={avatar.url} alt={avatar.name} className="w-full h-full object-cover" />
              {user.photoUrl === avatar.url && (
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                  <Check className="text-white" size={32} />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Segurança (Senha) */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-xl font-bold mb-4">Segurança</h2>
        {user.hasPassword ? (
          <p className="text-green-600 font-semibold flex items-center gap-2">
            <Check size={20} /> Você já possui uma senha configurada.
          </p>
        ) : (
          <form onSubmit={handleSavePassword} className="space-y-4">
            <p className="text-sm text-gray-600">
              Como você acessou usando rede social, pode cadastrar uma senha para usar o login com e-mail no futuro.
            </p>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Nova Senha</label>
              <input 
                type="password" 
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">Confirmar Senha</label>
              <input 
                type="password" 
                className="w-full border border-gray-300 rounded px-4 py-2 focus:ring-2 focus:ring-primary focus:outline-none"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="bg-dark text-light font-bold py-2 px-6 rounded hover:bg-gray-800 transition-colors">
              Salvar Senha
            </button>
          </form>
        )}
      </div>

    </div>
  );
}
