# 🚀 Master Geek (ERP/CRM O2O System)

O **Master Geek** é um sistema completo de gestão de varejo e relacionamento com o cliente (CRM) desenhado para o ecossistema Online-to-Offline (O2O). Desenvolvido inicialmente como um projeto de extensão universitária em Banco de Dados, ele resolve gargalos reais de operação em balcões de franquias físicas.

O foco da arquitetura é reduzir o atrito em vendas híbridas, automatizar processos manuais de relatórios e conectar o controle de estoque ao tráfego de clientes em tempo real através de agentes e visão computacional (IA).

### 🛠️ Core Tech Stack
* **Database & Auth:** Supabase (PostgreSQL) com Row Level Security (RLS).
* **Bot Engine (Piticão):** Automação no Telegram (Python/Node.js) para processamento OCR de notas fiscais (DANFE NFC-e) e baixas de estoque no balcão.
* **Comunicação Cliente:** Integração híbrida de WhatsApp (API Oficial 1:1 e WebSocket para automação de Comunidades VIP).
* **AI Integration:** Processamento de linguagem natural e visão computacional via Gemini API.
