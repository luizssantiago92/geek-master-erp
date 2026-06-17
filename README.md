# Master Geek & Piticas Rio - O2O Automation Platform

O **Master Geek** é um sistema completo de gestão de varejo e relacionamento com o cliente (CRM) desenhado para o ecossistema Online-to-Offline (O2O). Desenvolvido inicialmente como um projeto de extensão universitária em Banco de Dados, ele resolve gargalos reais de operação em balcões de franquias físicas.

O foco da arquitetura é reduzir o atrito em vendas híbridas, automatizar processos manuais de relatórios e conectar o controle de estoque ao tráfego de clientes em tempo real através de agentes e visão computacional (IA).

A plataforma se divide em três frentes principais:
1. **Banco de Dados & Autenticação:** Supabase (PostgreSQL) com Row Level Security (RLS).
2. **Chatbot Corporativo:** Piticão (Bot do Telegram com IA do Google Gemini).
3. **Plataforma Web (Vitrine e Dashboard):** Aplicação Next.js para clientes e administradores.

---

## 🏗️ Estrutura do Projeto

O repositório é um "monorepo", contendo múltiplas aplicações no mesmo lugar.

- `/piticao_bot/`: Código fonte do Piticão, o bot corporativo do Telegram feito em Python (`python-telegram-bot`).
- `/master_geek_web/`: Aplicação Web desenvolvida em Next.js (React) + TailwindCSS.
- `/*.sql`: Scripts de migração e estrutura do banco de dados relacional.
- `/*.md`: Documentação auxiliar, Requisitos do Produto (PRD) e Schemas.

---

## 🔒 Segurança de Dados (IMPORTANTE)

Este repositório foi configurado com um arquivo `.gitignore` rigoroso para proteger dados sensíveis.
**NUNCA comite arquivos que contenham:**
- Chaves de API (`GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`)
- Tokens de Bots de Telegram (`TELEGRAM_BOT_TOKEN`)
- Arquivos `.env` ou `.env.local`

Se você estiver clonando este projeto pela primeira vez, será necessário criar manualmente seus próprios arquivos `.env` nas respectivas pastas.

---

## 🚀 Como Executar

### 1. Banco de Dados (Supabase)
O projeto utiliza um banco Supabase em nuvem. As tabelas principais incluem `funcionarios`, `clientes`, e `produtos`. Os arquivos `.sql` na raiz do projeto servem como documentação das Queries DDL de inicialização.

### 2. Rodando o Bot (Telegram)
O bot do Telegram precisa de Python 3.10+ e utiliza a biblioteca do Gemini para interações com IA.

```bash
cd piticao_bot
# Crie e ative um ambiente virtual (venv)
python -m venv venv
venv\Scripts\activate
# Instale as dependências
pip install -r requirements.txt
# Rode o bot (lembre-se de configurar o arquivo .env primeiro)
python main.py
```

### 3. Rodando o Front-end Web (Next.js)
A plataforma Web atende clientes (Vitrine/Onboarding) e Gestores (Admin Dashboard).

```bash
cd master_geek_web
# Instale as dependências Node
npm install
# Inicie o servidor de desenvolvimento
npm run dev
```
Acesse `http://localhost:3000` no seu navegador.

---

## 🛠️ Tecnologias Utilizadas

- **Front-end:** Next.js 15, React, TailwindCSS, Lucide Icons.
- **Bot:** Python 3, `python-telegram-bot`, Google Generative AI (Gemini 2.5).
- **Backend/Database:** Supabase (PostgreSQL), Supabase Auth.
- **Comunicação Cliente:** Integração híbrida de WhatsApp (API Oficial 1:1 e WebSocket para automação de Comunidades VIP).

---

## 🤝 Contribuição
Siga as diretrizes de branch (`feature/nome-da-funcionalidade`) e utilize commits semânticos. Evite o commit direto na branch `main`.

Desenvolvido para Master Geek / Piticas.
