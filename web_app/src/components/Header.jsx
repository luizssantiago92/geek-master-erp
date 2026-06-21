import React, { useState } from 'react';
import { Search, ShoppingCart, Heart, User, Menu, Settings } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { useUser } from '../contexts/UserContext';

export default function Header() {
  const { totalItems, setIsCartOpen } = useCart();
  const { user, logout } = useUser();
  const navigate = useNavigate();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
    navigate('/');
  };

  return (
    <header className="bg-dark text-light sticky top-0 z-50 shadow-md">
      {/* Top Bar */}
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="bg-primary text-light font-bold text-2xl p-2 rounded-lg">
            Piticas
          </div>
          <span className="hidden md:block font-bold text-xl tracking-tight">Rio</span>
        </Link>

        {/* Search Bar */}
        <div className="flex-1 max-w-2xl mx-8 hidden md:flex">
          <div className="relative w-full">
            <input 
              type="text" 
              placeholder="O que você está procurando hoje?" 
              className="w-full bg-light text-dark py-2 pl-4 pr-10 rounded-full focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button className="absolute right-3 top-1/2 -translate-y-1/2 text-dark hover:text-primary">
              <Search size={20} />
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-6">
          <Link to="/admin" className="flex flex-col items-center hover:text-primary transition-colors text-yellow-400">
            <Settings size={24} />
            <span className="text-xs mt-1 hidden md:block">Admin</span>
          </Link>
          <Link to="/wishlist" className="flex flex-col items-center hover:text-primary transition-colors">
            <Heart size={24} />
            <span className="text-xs mt-1 hidden md:block">Desejos</span>
          </Link>
          <button onClick={() => setIsCartOpen(true)} className="flex flex-col items-center hover:text-primary transition-colors relative">
            <div className="relative">
              <ShoppingCart size={24} />
              {totalItems > 0 && (
                <span className="absolute -top-2 -right-2 bg-accent text-dark text-xs font-bold w-5 h-5 flex items-center justify-center rounded-full">
                  {totalItems}
                </span>
              )}
            </div>
            <span className="text-xs mt-1 hidden md:block">Reserva</span>
          </button>
          
          <div className="relative">
            {user ? (
              <div>
                <button 
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex flex-col items-center hover:text-primary transition-colors focus:outline-none"
                >
                  {user.photoUrl ? (
                    <img src={user.photoUrl} alt="Perfil" className="w-6 h-6 rounded-full object-cover border border-primary" />
                  ) : (
                    <User size={24} />
                  )}
                  <span className="text-xs mt-1 hidden md:block">{user.name?.split(' ')[0] || 'Usuário'}</span>
                </button>
                
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 text-dark border border-gray-100">
                    <div className="px-4 py-2 border-b border-gray-100 text-sm">
                      <p className="font-bold truncate">{user.name}</p>
                      <p className="text-gray-500 text-xs truncate">{user.email}</p>
                    </div>
                    <Link 
                      to="/conta" 
                      onClick={() => setIsUserMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Conferir Conta
                    </Link>
                    <button 
                      onClick={() => {
                        setIsUserMenuOpen(false);
                        alert("Alternando tema... (Apenas visual no protótipo)");
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Modo Escuro / Claro
                    </button>
                    <div className="border-t border-gray-100"></div>
                    <button 
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-semibold"
                    >
                      Deslogar (Sair)
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link to="/login" className="flex flex-col items-center hover:text-primary transition-colors">
                <User size={24} />
                <span className="text-xs mt-1 hidden md:block">Entrar</span>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Navigation (Sub-header) */}
      <nav className="bg-primary text-light hidden md:block">
        <div className="container mx-auto px-4">
          <ul className="flex items-center gap-8 py-2 text-sm font-semibold">
            <li><Link to="/categoria/funkos" className="hover:text-dark transition-colors">Funko Pop</Link></li>
            <li><Link to="/categoria/vestuario" className="hover:text-dark transition-colors">Vestuário Geek</Link></li>
            <li><Link to="/categoria/acessorios" className="hover:text-dark transition-colors">Acessórios</Link></li>
            <li><Link to="/categoria/decoracao" className="hover:text-dark transition-colors">Decoração</Link></li>
            <li><Link to="/colecoes" className="hover:text-dark transition-colors text-accent flex items-center gap-1">★ Coleções</Link></li>
          </ul>
        </div>
      </nav>

      {/* Mobile Search Bar (Visible only on mobile) */}
      <div className="md:hidden px-4 pb-3">
        <div className="relative w-full">
          <input 
            type="text" 
            placeholder="Buscar produtos..." 
            className="w-full bg-light text-dark py-2 pl-4 pr-10 rounded-full focus:outline-none"
          />
          <button className="absolute right-3 top-1/2 -translate-y-1/2 text-dark">
            <Search size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
