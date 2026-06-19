# Histórico de Atualizações (Changelog) - ERP Project

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

## [1.0.0] - 2026-06-17
### Fase 1 Finalizada: Chatbot Telegram (Piticão)

**🛠️ Mudanças Técnicas (Backend & Arquitetura)**
- Inicialização do servidor Python com `python-telegram-bot`.
- Integração completa com o **Supabase** (BaaS) com RLS e autenticação via JWT.
- Criação das tabelas `funcionarios`, `codigos_acesso` e `autorizacoes`.
- Integração com a API do **Google Gemini 1.5 Flash** para OCR de notas fiscais e conversas com personas (Lovable, Padrão, Sarcástica, etc).
- Implementação de arquitetura de Zero-Trust (Usuários desconhecidos são ignorados).
- Implementação do sistema de **Medalhões** (Gold e Silver) para aprovações em duas etapas.
- Implementação do "Simulador de Testes" em memória (`impersonation_states`) para o Administrador.
- Script assíncrono `broadcast_update.py` adicionado para disparos de Release Notes durante a madrugada.

**📱 Mudanças na Experiência do Usuário (UX)**
- **Novo Fluxo de Onboarding:** Novos vendedores precisam inserir um código de acesso único (ex: `PTC-1234Q`) para entrar no sistema.
- **Menus Interativos:** Cada cargo (Quiosque, Marketing, Boss, Admin) possui um teclado personalizado com apenas as funções que lhe cabem.
- **Sistema de Personas:** O usuário pode escolher a "personalidade" do robô para as conversas livres, gerando mais engajamento.
- **Modo Testador Avançado:** O Administrador possui um botão exclusivo para simular a visão de qualquer outro cargo, permitindo testes seguros sem alterar o banco de dados.
- **Avisos de Atualização:** Sempre que o sistema for atualizado, o bot avisará os funcionários e disponibilizará um botão `[ Saber Mais ]` com o resumo das novidades.

---
_Nota: A partir desta versão, o projeto se expande para a Fase 2 (Plataforma Web / Dashboard)._
