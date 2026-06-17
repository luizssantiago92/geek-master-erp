import Link from "next/link";
import { ChevronRight, Gamepad2, Search, ShoppingBag, User } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-piticas-dark text-white font-sans selection:bg-piticas-orange selection:text-white">
      {/* Navbar Minimalista (Estilo Netflix) */}
      <nav className="fixed top-0 w-full z-50 flex items-center justify-between px-8 py-6 bg-gradient-to-b from-black/80 to-transparent">
        <div className="flex items-center gap-2">
          <Gamepad2 className="text-piticas-orange w-8 h-8" />
          <h1 className="text-2xl font-black tracking-tighter">PITICAS<span className="text-piticas-orange">RIO</span></h1>
        </div>
        <div className="flex items-center gap-6">
          <Search className="w-5 h-5 text-gray-300 hover:text-white cursor-pointer transition-colors" />
          <ShoppingBag className="w-5 h-5 text-gray-300 hover:text-white cursor-pointer transition-colors" />
          <Link href="/login" className="flex items-center gap-2 bg-piticas-gray/50 hover:bg-piticas-gray border border-white/10 px-4 py-2 rounded-full transition-all">
            <User className="w-4 h-4" />
            <span className="text-sm font-semibold">Entrar</span>
          </Link>
        </div>
      </nav>

      {/* Hero Section (Fundo Escuro com Highlight Neon) */}
      <section className="relative h-screen flex flex-col justify-center items-center text-center px-4 overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-piticas-orange/20 blur-[120px] rounded-full mix-blend-screen pointer-events-none" />
        
        <div className="relative z-10 max-w-4xl mx-auto space-y-8">
          <div className="inline-block glass-panel px-4 py-1.5 mb-4 border-piticas-orange/30">
            <span className="text-piticas-orange font-bold text-sm tracking-wider uppercase">Nova Embaixada da Cultura Pop</span>
          </div>
          
          <h2 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9]">
            SUA SAGA <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-500">
              COMEÇA AQUI
            </span>
          </h2>
          
          <p className="text-xl md:text-2xl text-gray-400 font-medium max-w-2xl mx-auto">
            Reserve Funkos, camisetas e colecionáveis exclusivos. Retire no quiosque mais próximo e destrave prêmios.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
            <Link href="/catalogo" className="btn-primary text-lg px-8 py-4 flex items-center gap-2 w-full sm:w-auto justify-center">
              Explorar Catálogo
              <ChevronRight className="w-5 h-5" />
            </Link>
            <Link href="/comunidade" className="glass-panel text-white hover:bg-white/10 text-lg px-8 py-4 font-bold transition-all w-full sm:w-auto justify-center flex items-center">
              Entrar no Grupo VIP
            </Link>
          </div>
        </div>
      </section>

      {/* Categoria Destaque Section */}
      <section className="py-24 px-8 max-w-7xl mx-auto">
        <h3 className="text-3xl font-bold mb-12 flex items-center gap-3">
          <span className="w-2 h-8 bg-piticas-orange rounded-full block"></span>
          Tendências da Semana
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card Mockup 1 */}
          <div className="glass-panel p-6 group cursor-pointer hover:-translate-y-2 transition-transform duration-300">
            <div className="aspect-square bg-piticas-dark rounded-lg mb-4 flex items-center justify-center border border-white/5 relative overflow-hidden">
               {/* Simulando imagem */}
               <div className="absolute inset-0 bg-gradient-to-br from-piticas-gray to-piticas-dark"></div>
               <span className="relative z-10 text-gray-500 font-bold">Imagem Funko</span>
            </div>
            <span className="text-piticas-orange text-xs font-bold tracking-widest uppercase">Marvel</span>
            <h4 className="text-xl font-bold mt-1">Funko Pop Spider-Man</h4>
            <p className="text-gray-400 text-sm mt-2">Apenas para retirada em loja.</p>
          </div>

           {/* Card Mockup 2 */}
           <div className="glass-panel p-6 group cursor-pointer hover:-translate-y-2 transition-transform duration-300">
            <div className="aspect-square bg-piticas-dark rounded-lg mb-4 flex items-center justify-center border border-white/5 relative overflow-hidden">
               <div className="absolute inset-0 bg-gradient-to-br from-piticas-gray to-piticas-dark"></div>
               <span className="relative z-10 text-gray-500 font-bold">Imagem Camiseta</span>
            </div>
            <span className="text-piticas-orange text-xs font-bold tracking-widest uppercase">DC Comics</span>
            <h4 className="text-xl font-bold mt-1">Camiseta Batman Dark</h4>
            <p className="text-gray-400 text-sm mt-2">Apenas para retirada em loja.</p>
          </div>

           {/* Card Mockup 3 */}
           <div className="glass-panel p-6 group cursor-pointer hover:-translate-y-2 transition-transform duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-piticas-orange/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl pointer-events-none"></div>
            <div className="aspect-square bg-piticas-dark rounded-lg mb-4 flex items-center justify-center border border-white/5 relative overflow-hidden">
               <div className="absolute inset-0 bg-gradient-to-br from-piticas-gray to-piticas-dark"></div>
               <span className="relative z-10 text-gray-500 font-bold">Imagem Acessório</span>
            </div>
            <span className="text-piticas-orange text-xs font-bold tracking-widest uppercase">Star Wars</span>
            <h4 className="text-xl font-bold mt-1">Caneca Darth Vader</h4>
            <p className="text-gray-400 text-sm mt-2">Apenas para retirada em loja.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
