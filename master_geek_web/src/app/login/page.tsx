'use client'

import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { createClient } from '@/utils/supabase/client'
import { Gamepad2, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function Login() {
  const supabase = createClient()

  return (
    <main className="min-h-screen bg-piticas-dark text-white font-sans flex items-center justify-center p-4 relative overflow-hidden">
      {/* Efeito de Luz */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-piticas-orange/10 blur-[100px] rounded-full pointer-events-none" />
      
      <Link href="/" className="absolute top-8 left-8 text-gray-400 hover:text-white flex items-center gap-2 transition-colors z-20">
        <ArrowLeft className="w-5 h-5" />
        Voltar para o Catálogo
      </Link>

      <div className="glass-panel w-full max-w-md p-8 relative z-10 flex flex-col items-center">
        <div className="flex items-center gap-2 mb-8">
          <Gamepad2 className="text-piticas-orange w-8 h-8" />
          <h1 className="text-2xl font-black tracking-tighter">PITICAS<span className="text-piticas-orange">RIO</span></h1>
        </div>

        <div className="w-full">
          <h2 className="text-xl font-bold mb-6 text-center">Acesse seu perfil VIP</h2>
          
          <Auth
            supabaseClient={supabase}
            appearance={{ 
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#FF5A00',
                    brandAccent: '#e55100',
                    inputText: 'white',
                    inputBackground: '#1A1A1A',
                    inputBorder: '#333333',
                  }
                }
              },
              className: {
                container: 'w-full',
                button: 'rounded-md py-3 font-bold',
                input: 'rounded-md px-4 py-3 bg-piticas-gray border-white/10 text-white',
                label: 'text-gray-300 font-medium',
              }
            }}
            providers={['google', 'facebook']}
            theme="dark"
            localization={{
              variables: {
                sign_in: {
                  email_label: 'Endereço de E-mail',
                  password_label: 'Sua Senha Mágica',
                  button_label: 'Entrar na Área VIP',
                  social_provider_text: 'Entrar com {{provider}}',
                  link_text: 'Já tem conta? Entre aqui',
                },
                sign_up: {
                  email_label: 'Endereço de E-mail',
                  password_label: 'Crie uma Senha Mágica',
                  button_label: 'Criar Perfil VIP',
                  social_provider_text: 'Cadastrar com {{provider}}',
                  link_text: 'Não tem conta? Cadastre-se',
                }
              }
            }}
          />
        </div>
      </div>
    </main>
  )
}
