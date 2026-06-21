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

function App() {
  return (
    <UserProvider>
      <CartProvider>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col font-sans bg-gray-50">
            <Header />
            <Minicart />
            
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
                {/* Outras rotas entrarão aqui */}
              </Routes>
            </main>

            <Footer />
          </div>
        </BrowserRouter>
      </CartProvider>
    </UserProvider>
  );
}

export default App;
