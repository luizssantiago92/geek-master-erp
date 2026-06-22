-- ==============================================================================
-- GEEK MASTER - SCRIPT DE INICIALIZAÇÃO DE BANCO DE DADOS ATIVO (SUPABASE)
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------------------------------------------------
-- 1. IDENTIDADE E CONTROLE DE ACESSO
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.funcionarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    cargo TEXT,
    nivel_acesso INTEGER CHECK (nivel_acesso >= 1 AND nivel_acesso <= 4),
    ativo BOOLEAN DEFAULT true,
    medalhao TEXT DEFAULT 'Bronze',
    perfis_teste JSONB DEFAULT '[]'::jsonb,

    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.codigos_acesso (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo TEXT UNIQUE NOT NULL,
    cargo TEXT NOT NULL,
    nivel_acesso INTEGER NOT NULL,
    usado BOOLEAN DEFAULT false,
    criado_por UUID REFERENCES public.funcionarios(id),
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    expira_em TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.autorizacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    solicitante_id UUID REFERENCES public.funcionarios(id),
    acao TEXT NOT NULL,
    status TEXT DEFAULT 'PENDENTE',
    data_solicitacao TIMESTAMPTZ DEFAULT NOW(),
    data_resposta TIMESTAMPTZ,
    aprovador_id UUID REFERENCES public.funcionarios(id)
);

CREATE TABLE IF NOT EXISTS public.sessoes_magicas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    funcionario_id UUID REFERENCES public.funcionarios(id),
    token_sessao TEXT UNIQUE NOT NULL,
    usado BOOLEAN DEFAULT false,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    expira_em TIMESTAMPTZ
);

-----------------------------------------------------------------------
-- 2. CLIENTES E PRODUTOS
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    telefone TEXT,
    cpf TEXT UNIQUE,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.produtos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ean TEXT UNIQUE,
    nome TEXT NOT NULL,
    franquia TEXT,
    imagem_url TEXT,
    imagens_galeria JSONB DEFAULT '[]'::jsonb,
    preco_base NUMERIC(10,2) DEFAULT 0.0,
    descricao TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    is_new BOOLEAN DEFAULT false,
    is_teste BOOLEAN DEFAULT false,
    status_publicacao TEXT DEFAULT 'PENDENTE',
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.estoque (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id UUID REFERENCES public.produtos(id) ON DELETE CASCADE,
    quiosque_id UUID REFERENCES public.funcionarios(id) ON DELETE CASCADE,
    quantidade INTEGER DEFAULT 0 CHECK (quantidade >= 0),
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(produto_id, quiosque_id)
);

-----------------------------------------------------------------------
-- 3. CATÁLOGO MESTRE E SINCRONIZAÇÃO DE FORNECEDORES
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.catalogo_fornecedores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_externo TEXT NOT NULL,
    nome TEXT NOT NULL,
    ean TEXT,
    preco NUMERIC(10, 2),
    imagem_url TEXT,
    descricao TEXT,
    origem TEXT NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(origem, id_externo)
);

-----------------------------------------------------------------------
-- 4. TRANSAÇÕES E PEDIDOS
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.encomendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES public.clientes(id),
    quiosque_id UUID REFERENCES public.funcionarios(id),
    valor_total NUMERIC(10,2) DEFAULT 0.0,
    status TEXT DEFAULT 'PENDENTE',
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.encomendas_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encomenda_id UUID REFERENCES public.encomendas(id) ON DELETE CASCADE,
    produto_id UUID REFERENCES public.produtos(id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL
);

-----------------------------------------------------------------------
-- 5. INTEGRAÇÕES, NOTIFICAÇÕES E RANKINGS
-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.notificacoes_bot (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tipo TEXT NOT NULL,
    conteudo JSONB NOT NULL,
    lido BOOLEAN DEFAULT false,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);



CREATE TABLE IF NOT EXISTS public.lista_desejos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES public.clientes(id) ON DELETE CASCADE,
    produto_id UUID REFERENCES public.produtos(id) ON DELETE CASCADE,
    notificado BOOLEAN DEFAULT false,
    adicionado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(cliente_id, produto_id)
);

-----------------------------------------------------------------------
-- ÍNDICES PARA PERFORMANCE
-----------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_funcionarios_telegram ON public.funcionarios(telegram_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_magicas_token ON public.sessoes_magicas(token_sessao);
CREATE INDEX IF NOT EXISTS idx_estoque_produto ON public.estoque(produto_id);
CREATE INDEX IF NOT EXISTS idx_estoque_quiosque ON public.estoque(quiosque_id);
CREATE INDEX IF NOT EXISTS idx_catalogo_fornecedores_ean ON public.catalogo_fornecedores(ean);
CREATE INDEX IF NOT EXISTS idx_encomendas_cliente ON public.encomendas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_encomendas_quiosque ON public.encomendas(quiosque_id);
CREATE INDEX IF NOT EXISTS idx_encomendas_items_encomenda ON public.encomendas_items(encomenda_id);
CREATE INDEX IF NOT EXISTS idx_lista_desejos_produto ON public.lista_desejos(produto_id);

-- ==============================================================================
-- FIM DO SCRIPT DE SCHEMA
-- ==============================================================================
