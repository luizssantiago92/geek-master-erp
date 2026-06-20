import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 pt-12 pb-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="bg-primary text-light font-bold text-2xl p-2 rounded-lg inline-block mb-4">
              Piticão
            </div>
            <p className="text-sm text-gray-500 leading-relaxed">
              O seu catálogo O2O definitivo. 
              Reserve online e retire no quiosque mais próximo de você com toda a comodidade.
            </p>
          </div>
          
          <div>
            <h4 className="font-bold text-dark mb-4 text-lg">Sobre</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link to="/como-funciona" className="hover:text-primary">Como Funciona (Retirada)</Link></li>
              <li><Link to="/quiosques" className="hover:text-primary">Nossos Quiosques</Link></li>
              <li><Link to="/termos" className="hover:text-primary">Termos e Condições</Link></li>
              <li><Link to="/privacidade" className="hover:text-primary">Políticas de Privacidade</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-dark mb-4 text-lg">Produtos</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link to="/categoria/funkos" className="hover:text-primary">Funko Pop</Link></li>
              <li><Link to="/categoria/vestuario" className="hover:text-primary">Vestuário Geek</Link></li>
              <li><Link to="/categoria/acessorios" className="hover:text-primary">Acessórios</Link></li>
              <li><Link to="/categoria/decoracao" className="hover:text-primary">Decoração</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-dark mb-4 text-lg">Atendimento</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link to="/faq" className="hover:text-primary">Dúvidas Frequentes (FAQ)</Link></li>
              <li><Link to="/contato" className="hover:text-primary">Fale Conosco</Link></li>
              <li><a href="#" className="hover:text-primary font-semibold">WhatsApp: (21) 99999-9999</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-8 flex flex-col md:flex-row items-center justify-between">
          <p className="text-xs text-gray-400">
            © {new Date().getFullYear()} Piticão Geek Store - Apenas Catálogo para Retirada (Click & Collect)
          </p>
          <div className="flex gap-4 mt-4 md:mt-0 text-sm font-semibold text-gray-500">
            <span>Pagamento Exclusivo na Retirada</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
