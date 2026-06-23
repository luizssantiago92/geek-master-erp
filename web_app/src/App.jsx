import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CartProvider } from './contexts/CartContext';
import { UserProvider } from './contexts/UserContext';
import Header from './components/Header';
import Footer from './components/Footer';
import Minicart from './components/Minicart';
import Home from './pages/Home';
import Login from './pages/Login';
import Onboarding from './pages/Onboarding';
import Checkout from './pages/Checkout';
import CompletarCadastro from './pages/CompletarCadastro';
import Conta from './pages/Conta';
import ProductDetails from './pages/ProductDetails';
import AdminCatalog from './pages/AdminCatalog';

import { useTelegram } from './hooks/useTelegram';

function AppContent() {
  const { isTelegram } = useTelegram();

  return (
    <div className={`min-h-screen flex flex-col font-sans ${isTelegram ? 'bg-white' : 'bg-gray-50'}`}>
      {!isTelegram && <Header />}
      {!isTelegram && <Minicart />}
      
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/completar-cadastro" element={<CompletarCadastro />} />
          <Route path="/conta" element={<Conta />} />
          <Route path="/produto/:id" element={<ProductDetails />} />
          <Route path="/admin" element={<AdminCatalog />} />
        </Routes>
      </main>

      {!isTelegram && <Footer />}
    </div>
  );
}

function App() {
  return (
    <UserProvider>
      <CartProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </CartProvider>
    </UserProvider>
  );
}

export default App;
