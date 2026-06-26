# Geek Master - ERP O2O & Automação de Varejo com IA

O **Geek Master** é um ecossistema completo de gestão de varejo (ERP) desenhado para o modelo Online-to-Offline (O2O). Desenvolvido inicialmente como um projeto prático de graduação em Banco de Dados, ele resolve gargalos operacionais reais e diários na linha de frente de franquias físicas.

O foco da arquitetura é reduzir o atrito tecnológico para as equipes de vendas, automatizar processos manuais de entrada de produtos e engajar os colaboradores através da gamificação de metas, conectando o "chão de loja" aos gestores em tempo real.

A plataforma se divide em três frentes principais:
1. **Banco de Dados & Autenticação:** Supabase (PostgreSQL) com segurança estrita via Row Level Security (RLS).
2. **Assistente Corporativo (Bot):** Piticão (Bot do Telegram impulsionado por Inteligência Artificial do Google Gemini).
3. **Plataforma Web (Mini Apps):** Aplicações em React integradas nativamente ao Telegram para revisão e publicação de catálogos.

---

## 🏗️ Estrutura do Projeto

O repositório é um "monorepo", contendo múltiplas aplicações no mesmo lugar.

- `/piticao_bot/`: Código fonte do Piticão, o bot corporativo feito em Python (`python-telegram-bot`). Responsável por processar Visão Computacional (leitura de produtos) e Web Scraping.
- `/web_app/`: Aplicação Web desenvolvida em React, Vite e TailwindCSS, operando também como um Telegram Mini App.
- `/docs_master/`: Fonte Única de Verdade (Single Source of Truth) contendo toda a documentação auxiliar, PRDs e planos arquiteturais.

---

## 🔒 Segurança de Dados (IMPORTANTE)

Este repositório foi configurado com um arquivo `.gitignore` rigoroso para proteger dados sensíveis.
**NUNCA comite arquivos que contenham:**
- Chaves de API (`GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`)
- Tokens de Bots do Telegram (`TELEGRAM_BOT_TOKEN`)
- Arquivos `.env` ou `.env.local`

Se você estiver clonando este projeto pela primeira vez, será necessário criar manualmente seus próprios arquivos `.env` nas respectivas pastas.

---

🛠️ Tecnologias e Funcionalidades de Destaque
Visão Computacional e Scraping: Os funcionários fotografam os produtos físicos (ex: Funko Pops). A IA (Gemini) lê a caixa, extrai franquia/número, faz o cruzamento via web scraping e importa fotos e dados oficiais automaticamente.
Engajamento e Gamificação: Rastreamento de metas e pontuação de vendedores atualizada em tempo real via Supabase.
Front-end: React, Vite, TailwindCSS, Lucide Icons e SDK do Telegram Mini Apps.
Bot: Python 3, python-telegram-bot, Google Generative AI (Gemini 1.5).
Backend/Database: Supabase (PostgreSQL), Supabase Auth e Policies (RLS).
🤖 Construído com Inteligência Artificial (Orquestração e Arquitetura)
Este projeto tem a particularidade de ter sido inteiramente construído de forma orquestrada com IA, utilizando o Google Gemini integrado aos agentes do Antigravity IDE (Vibe Coding).

Minha contribuição central para este projeto atua na união entre o Mundo de Negócios e a Arquitetura de Software:

Desenhei a visão macro do ecossistema mapeando os gargalos reais do varejo.
Orquestrei a conexão entre as ferramentas essenciais: Supabase (segurança), Telegram/React (front-end Híbrido) e automações em Python.
Forneci os contextos, PRDs, prompts estruturados e guiei a Inteligência Artificial na execução técnica e na implementação dos códigos.
O uso coordenado dessas ferramentas reflete uma abordagem moderna de desenvolvimento de software colaborativo (Humano + IA), onde a visão de mercado e a arquitetura estratégica ditam o ritmo da automação.
