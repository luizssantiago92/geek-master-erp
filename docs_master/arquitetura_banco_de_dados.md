# 🗄️ Arquitetura do Banco de Dados (Supabase PostgreSQL)

Este documento centraliza as diretrizes, a estrutura de tabelas e as configurações de segurança implementadas no Supabase do projeto Geek Master.

---

## 1. Visão Geral do Paradigma de Autenticação

Para garantir a agilidade de um **MVP (Minimum Viable Product)** com integração total ao Bot do Telegram, a arquitetura de acesso adotou um modelo de **Autenticação Desacoplada (Magic Links)**.

Isso significa que:
- O **Bot do Telegram (Python)** conecta ao banco via *Service Role Key* (ignorando as Row Level Securities do banco) e atua como o motor de regras de negócio.
- O **Painel React (Web App)** consome os dados via *Anon Key* e possui uma trava de segurança em nível de aplicação (Frontend). O acesso é feito via token de sessão temporal (`sessoes_magicas`) gerado pelo Bot.
- Devido a este design, as políticas **RLS (Row Level Security)** das tabelas operadas pelo React App (produtos, encomendas, notificações, sessões, clientes) possuem regras permissivas de leitura/escrita. 
- ⚠️ **AVISO DE SEGURANÇA (ROADMAP):** O modelo atual assume a confiança do *anon key* como chave de operação do frontend. Para futuras expansões Enterprise, a migração para **JWT Nativo do Supabase Auth** deverá ser planejada para transferir as restrições do frontend de volta para as *Policies* do PostgreSQL.

---

## 2. Mapa de Tabelas Ativas

A base de dados atualizada e simplificada (consolidada no script `docs/database/01_master_schema.sql`) é composta pelas seguintes áreas de domínio:

### 2.1. Identidade e Acesso (Gerenciado pelo Bot)
- **`funcionarios`**: Armazena os colaboradores da Geek Master. Inclui cargos, IDs do Telegram, e os *Níveis de Acesso* (1 = Quiosque, 2 = Marketing, 3 = Boss, 4 = ADM).
- **`codigos_acesso`**: Códigos gerados pelo comando de "Modo de Testador" ou cadastro interno. Controla tempo de expiração e o cargo que será concedido ao usuário.
- **`autorizacoes`**: Permissões de exceção (ex: ações limitadas autorizadas por usuários "Gold").
- **`sessoes_magicas`**: Tabela ponte. O bot salva um token (UUID), e o painel React o lê, valida e o marca como "usado" (auto-destruição).

### 2.2. Catálogo e Operações
- **`produtos`**: Catálogo mestre de action figures e itens Geek (com suporte a `is_new`, `is_teste`, e galerias JSONB para a vitrine virtual).
- **`estoque`**: Relação *N:N* controlando a quantidade de cada `produto` que está alocada sob a guarda de um `quiosque_id` (funcionário).
- **`clientes`**: Dados dos clientes finais e fãs da Geek Master (com validação de CPF e Contato).

### 2.3. Catálogo Mestre (Fornecedores Oficiais)
- **`catalogo_fornecedores`**: Banco de dados alimentado automaticamente via scripts de sincronização (`catalog_sync.py`) lendo APIs VTEX. Ele clona as informações oficiais de preços, imagens e códigos de barra de lojas como Piticas, Zona Criativa e Moça do Pop para acelerar o processo de inteligência artificial do chatbot.

### 2.4. Transações Financeiras
- **`encomendas`**: Controle macro de compras. Possui status de rastreio (`PENDENTE`, `RETIRADA`), vinculando o cliente e o responsável (Quiosque).
- **`encomendas_items`**: Tabela relacional das compras, especificando `produto_id` e quantidades para cada encomenda.

### 2.4. Integração e Alertas (Event-Driven)
- **`notificacoes_bot`**: Tabela fila/queue. O painel React insere registros nela ("Solicitar Publicação"). Um worker no servidor Python (`check_notificacoes()`) monitora esta tabela constantemente. Assim que um registro surge, o Bot notifica o gestor via Telegram e marca a linha como lida.

---

## 3. Melhorias de Performance Implementadas

De acordo com as boas práticas de otimização de banco de dados e as varreduras de sistema:
- **Indexação (Indexes):** Criamos múltiplos Índices B-Tree (ex: `idx_encomendas_cliente_id`) nas chaves estrangeiras. No Postgres, FKs (Foreign Keys) não geram índices automaticamente. Aplicá-los previne *Table Scans* lentos durante o JOIN entre `clientes` e `encomendas`.
- **Prevenção de Locks e Descarte de Código:** Limpeza do diretório de schemas, extinguindo as tabelas fantasmas que não faziam parte do fluxo ativo do código Python/React, focando 100% no schema funcional homologado.

> [!TIP]
> Caso seja necessário recriar o banco do zero ou fazer deploy em um ambiente Staging, o arquivo definitivo a ser executado no painel SQL do Supabase encontra-se em `docs/database/01_master_schema.sql`.
