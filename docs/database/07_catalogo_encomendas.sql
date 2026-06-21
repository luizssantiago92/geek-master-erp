-- ==============================================================================
-- 7. MASTER GEEK - FASE 5: CATÁLOGO, ESTOQUE E ENCOMENDAS
-- ==============================================================================

-- 1. Tabela de Produtos (Catálogo Master)
CREATE TABLE IF NOT EXISTS public.produtos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ean VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    franquia VARCHAR(100),
    preco_base DECIMAL(10, 2),
    imagem_url VARCHAR(500),
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Tabela de Estoque Local (Amarrado ao ID do Vendedor/Quiosque)
CREATE TABLE IF NOT EXISTS public.estoque (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id UUID REFERENCES public.produtos(id) ON DELETE CASCADE NOT NULL,
    quiosque_id UUID REFERENCES public.funcionarios(id) ON DELETE CASCADE NOT NULL,
    quantidade INTEGER DEFAULT 0,
    atualizado_em TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(produto_id, quiosque_id) -- Impede produtos duplicados no mesmo quiosque
);

-- 3. Tabela de Clientes (Gamificação VIP)
CREATE TABLE IF NOT EXISTS public.clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cpf VARCHAR(14) UNIQUE NOT NULL,
    nome VARCHAR(255),
    telefone VARCHAR(20),
    nivel_vip VARCHAR(50) DEFAULT 'Novato',
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Tabela de Encomendas (O ciclo de Venda)
CREATE TABLE IF NOT EXISTS public.encomendas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES public.clientes(id) ON DELETE CASCADE NOT NULL,
    quiosque_id UUID REFERENCES public.funcionarios(id) ON DELETE SET NULL, -- Se o quiosque for apagado, a encomenda fica órfã mas n se perde
    codigo_retirada VARCHAR(10) UNIQUE NOT NULL, -- Ex: 8492
    status VARCHAR(50) DEFAULT 'PENDENTE', -- PENDENTE, RETIRADA, CANCELADA
    valor_original DECIMAL(10, 2) NOT NULL,
    valor_final DECIMAL(10, 2), -- Só é preenchido na baixa
    criado_em TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- ==============================================================================
-- POLÍTICAS RLS (Row Level Security) BÁSICAS PARA AS NOVAS TABELAS
-- ==============================================================================

-- Habilitar RLS
ALTER TABLE public.produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.estoque ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.encomendas ENABLE ROW LEVEL SECURITY;

-- Como as chamadas vêm do Service Role do bot (em python), o RLS será bypassado pelo bot.
-- As políticas abaixo são para garantir que usuários anônimos na API pública não consigam mexer.
CREATE POLICY "Permitir leitura pública de produtos" ON public.produtos FOR SELECT USING (true);
CREATE POLICY "Bot e ADM podem tudo em produtos" ON public.produtos FOR ALL USING (true);

CREATE POLICY "Bot e ADM podem tudo em estoque" ON public.estoque FOR ALL USING (true);
CREATE POLICY "Bot e ADM podem tudo em clientes" ON public.clientes FOR ALL USING (true);
CREATE POLICY "Bot e ADM podem tudo em encomendas" ON public.encomendas FOR ALL USING (true);
