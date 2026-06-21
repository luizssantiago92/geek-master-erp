-- ==============================================================================
-- MASTER GEEK - SCRIPT DE INICIALIZAÇÃO DE BANCO DE DADOS (SUPABASE/POSTGRESQL)
-- ==============================================================================

-- Habilita a extensão para geração de UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. Tabela: funcionarios (Domínio de Identidade)
-- ==========================================
CREATE TABLE public.funcionarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    cargo TEXT,
    -- Restringe o nível de acesso entre 1 (Quiosque) e 4 (ADM)
    nivel_acesso INTEGER CHECK (nivel_acesso >= 1 AND nivel_acesso <= 4),
    -- Identificador único do bot Piticão no Telegram
    telegram_id TEXT UNIQUE, 
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS OBRIGATÓRIO
ALTER TABLE public.funcionarios ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 2. Tabela: clientes_vip (Domínio de Identidade)
-- ==========================================
CREATE TABLE public.clientes_vip (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    telefone_whatsapp TEXT,
    -- CPF deve ser único no sistema para garantir integridade e cruzar com nota fiscal
    cpf TEXT UNIQUE NOT NULL,
    -- JSONB para armazenar preferências variadas de forma flexível (ex: ["Star Wars", "Marvel"])
    preferencias_tags JSONB DEFAULT '{}'::jsonb, 
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS OBRIGATÓRIO
ALTER TABLE public.clientes_vip ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 3. Tabela: produtos_catalogo (Domínio de Catálogo)
-- ==========================================
CREATE TABLE public.produtos_catalogo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ean TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    -- URLs apontando para o Storage (ex: bucket do Supabase), NUNCA base64
    url_imagem TEXT, 
    categoria TEXT,
    status_raspagem TEXT DEFAULT 'pendente',
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS OBRIGATÓRIO
ALTER TABLE public.produtos_catalogo ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 4. Tabela: pedidos_encomenda (Domínio de Transação)
-- ==========================================
CREATE TABLE public.pedidos_encomenda (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- FK: Todo pedido precisa de um cliente válido. Cascade remove pedidos se cliente for deletado.
    cliente_id UUID NOT NULL REFERENCES public.clientes_vip(id) ON DELETE CASCADE, 
    -- FK: Todo pedido vincula um produto do catálogo.
    produto_id UUID NOT NULL REFERENCES public.produtos_catalogo(id) ON DELETE RESTRICT, 
    -- Status baseados no PRD
    status TEXT CHECK (status IN ('pendente', 'aguardando_retirada', 'concluida_com_divergencia', 'concluida_integral')) DEFAULT 'pendente',
    codigo_retirada VARCHAR(4) NOT NULL,
    valor_final NUMERIC(10,2),
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Habilitar RLS OBRIGATÓRIO
ALTER TABLE public.pedidos_encomenda ENABLE ROW LEVEL SECURITY;


-- ==============================================================================
-- POLÍTICAS DE SEGURANÇA (ROW LEVEL SECURITY - RLS)
-- ==============================================================================

-- Função utilitária para verificar se quem faz a requisição é um funcionário válido
-- Pressupõe que a autenticação (auth.uid()) mapeia para a tabela de funcionarios.
CREATE OR REPLACE FUNCTION public.is_funcionario() RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.funcionarios WHERE id = auth.uid()
  );
$$ LANGUAGE sql SECURITY DEFINER;


-- ------------------------------------------------------------------------------
-- Políticas para: funcionarios
-- ------------------------------------------------------------------------------
-- Apenas funcionários podem visualizar outros funcionários.
CREATE POLICY "Funcionários podem ler outros funcionários"
ON public.funcionarios FOR SELECT
USING (public.is_funcionario());


-- ------------------------------------------------------------------------------
-- Políticas para: clientes_vip
-- ------------------------------------------------------------------------------
-- Funcionários podem ver todos os clientes
CREATE POLICY "Funcionários podem ler todos os clientes"
ON public.clientes_vip FOR SELECT
USING (public.is_funcionario());

-- Clientes logados só podem ver o próprio perfil
CREATE POLICY "Clientes logados podem ler os próprios dados"
ON public.clientes_vip FOR SELECT
USING (auth.uid() = id);

-- Clientes logados só podem editar o próprio perfil
CREATE POLICY "Clientes logados podem atualizar os próprios dados"
ON public.clientes_vip FOR UPDATE
USING (auth.uid() = id);


-- ------------------------------------------------------------------------------
-- Políticas para: produtos_catalogo
-- ------------------------------------------------------------------------------
-- Catálogo Web Dinâmico: qualquer um (logado ou anônimo) pode ver produtos
CREATE POLICY "Qualquer pessoa pode ler produtos do catálogo"
ON public.produtos_catalogo FOR SELECT
USING (true);

-- Apenas funcionários/sistemas internos (como o Piticão via API) podem gerenciar o catálogo
CREATE POLICY "Apenas funcionários gerenciam produtos"
ON public.produtos_catalogo FOR ALL
USING (public.is_funcionario());


-- ------------------------------------------------------------------------------
-- Políticas para: pedidos_encomenda
-- ------------------------------------------------------------------------------
-- Funcionários no balcão e Bot Piticão precisam de acesso total às encomendas
CREATE POLICY "Funcionários podem ler e escrever todos os pedidos"
ON public.pedidos_encomenda FOR ALL
USING (public.is_funcionario());

-- Clientes no app/web só enxergam as encomendas que eles mesmos fizeram
CREATE POLICY "Clientes podem ler os próprios pedidos"
ON public.pedidos_encomenda FOR SELECT
USING (auth.uid() = cliente_id);

-- Clientes podem criar suas próprias encomendas no catálogo
CREATE POLICY "Clientes podem criar os próprios pedidos"
ON public.pedidos_encomenda FOR INSERT
WITH CHECK (auth.uid() = cliente_id);
